package server

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/sipeed/picoclaw/pkg/auth"
	"github.com/sipeed/picoclaw/pkg/config"
	"github.com/sipeed/picoclaw/pkg/providers"
)

const DefaultPort = "18800"

// providerStatus represents the auth status of a single provider in API responses.
type providerStatus struct {
	Provider   string `json:"provider"`
	AuthMethod string `json:"auth_method"`
	Status     string `json:"status"`
	AccountID  string `json:"account_id,omitempty"`
	Email      string `json:"email,omitempty"`
	ProjectID  string `json:"project_id,omitempty"`
	ExpiresAt  string `json:"expires_at,omitempty"`
}

type modelTestRequest struct {
	Model config.ModelConfig `json:"model"`
}

type modelTestResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Model   string `json:"model,omitempty"`
	Preview string `json:"preview,omitempty"`
}

// ── Route registration ───────────────────────────────────────────

func RegisterConfigAPI(mux *http.ServeMux, absPath string) {
	// GET /api/config — read config
	mux.HandleFunc("GET /api/config", func(w http.ResponseWriter, r *http.Request) {
		cfg, err := config.LoadConfig(absPath)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to load config: %v", err), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		resp := map[string]any{
			"config": cfg,
			"path":   absPath,
		}
		enc := json.NewEncoder(w)
		enc.SetIndent("", "  ")
		if err := enc.Encode(resp); err != nil {
			log.Printf("Failed to encode response: %v", err)
		}
	})

	// PUT /api/config — save config
	mux.HandleFunc("PUT /api/config", func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(io.LimitReader(r.Body, 1<<20))
		if err != nil {
			http.Error(w, "Failed to read request body", http.StatusBadRequest)
			return
		}
		defer r.Body.Close()

		var cfg config.Config
		if err := json.Unmarshal(body, &cfg); err != nil {
			http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
			return
		}

		if err := config.SaveConfig(absPath, &cfg); err != nil {
			http.Error(w, fmt.Sprintf("Failed to save config: %v", err), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	// POST /api/config/test-model — test model connectivity before saving config
	mux.HandleFunc("POST /api/config/test-model", func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(io.LimitReader(r.Body, 1<<20))
		if err != nil {
			http.Error(w, "Failed to read request body", http.StatusBadRequest)
			return
		}
		defer r.Body.Close()

		var req modelTestRequest
		if err := json.Unmarshal(body, &req); err != nil {
			http.Error(w, fmt.Sprintf("Invalid JSON: %v", err), http.StatusBadRequest)
			return
		}

		req.Model.ModelName = strings.TrimSpace(req.Model.ModelName)
		req.Model.Model = strings.TrimSpace(req.Model.Model)
		req.Model.APIKey = strings.TrimSpace(req.Model.APIKey)
		req.Model.APIBase = strings.TrimSpace(req.Model.APIBase)
		req.Model.Proxy = strings.TrimSpace(req.Model.Proxy)
		req.Model.AuthMethod = strings.TrimSpace(req.Model.AuthMethod)
		req.Model.ConnectMode = strings.TrimSpace(req.Model.ConnectMode)
		req.Model.Workspace = strings.TrimSpace(req.Model.Workspace)

		if req.Model.Model == "" {
			http.Error(w, "model is required", http.StatusBadRequest)
			return
		}

		provider, modelID, err := providers.CreateProviderFromConfig(&req.Model)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to create provider: %v", err), http.StatusBadRequest)
			return
		}
		if closer, ok := provider.(providers.StatefulProvider); ok {
			defer closer.Close()
		}

		ctx, cancel := context.WithTimeout(r.Context(), 20*time.Second)
		defer cancel()

		resp, err := provider.Chat(ctx, []providers.Message{{Role: "user", Content: "Reply with exactly: OK"}}, nil, modelID, map[string]any{
			"max_tokens":  32,
			"temperature": 0,
		})
		if err != nil {
			http.Error(w, fmt.Sprintf("Connectivity test failed: %v", err), http.StatusBadGateway)
			return
		}

		preview := ""
		if resp != nil {
			preview = strings.TrimSpace(resp.Content)
		}
		if len(preview) > 120 {
			preview = preview[:120] + "..."
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(modelTestResponse{
			Status:  "ok",
			Message: "Connectivity test passed",
			Model:   modelID,
			Preview: preview,
		})
	})
}

func RegisterAuthAPI(mux *http.ServeMux, absPath string) {
	// GET /api/auth/status — all authenticated providers + pending login state
	mux.HandleFunc("GET /api/auth/status", func(w http.ResponseWriter, r *http.Request) {
		store, err := auth.LoadStore()
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to load auth store: %v", err), http.StatusInternalServerError)
			return
		}

		result := []providerStatus{}
		for name, cred := range store.Credentials {
			status := "active"
			if cred.IsExpired() {
				status = "expired"
			} else if cred.NeedsRefresh() {
				status = "needs_refresh"
			}
			ps := providerStatus{
				Provider:   name,
				AuthMethod: cred.AuthMethod,
				Status:     status,
				AccountID:  cred.AccountID,
				Email:      cred.Email,
				ProjectID:  cred.ProjectID,
			}
			if !cred.ExpiresAt.IsZero() {
				ps.ExpiresAt = cred.ExpiresAt.Format(time.RFC3339)
			}
			result = append(result, ps)
		}

		// Include pending device code state
		var pendingDevice map[string]any
		activeDeviceSessionMu.Lock()
		if activeDeviceSession != nil {
			activeDeviceSession.mu.Lock()
			pendingDevice = map[string]any{
				"provider":   activeDeviceSession.Provider,
				"status":     activeDeviceSession.Status,
				"device_url": activeDeviceSession.Info.VerifyURL,
				"user_code":  activeDeviceSession.Info.UserCode,
			}
			if activeDeviceSession.Error != "" {
				pendingDevice["error"] = activeDeviceSession.Error
			}
			if activeDeviceSession.Done {
				activeDeviceSession.mu.Unlock()
				activeDeviceSession = nil
			} else {
				activeDeviceSession.mu.Unlock()
			}
		}
		activeDeviceSessionMu.Unlock()

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]any{
			"providers":      result,
			"pending_device": pendingDevice,
		})
	})

	// POST /api/auth/login — initiate provider login
	mux.HandleFunc("POST /api/auth/login", func(w http.ResponseWriter, r *http.Request) {
		var req struct {
			Provider string `json:"provider"`
			Token    string `json:"token,omitempty"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		switch req.Provider {
		case "openai":
			handleOpenAILogin(w, absPath)
		case "anthropic":
			handleAnthropicLogin(w, req.Token, absPath)
		case "google-antigravity", "antigravity":
			handleGoogleAntigravityLogin(w, r, absPath)
		default:
			http.Error(
				w,
				fmt.Sprintf(
					"Unsupported provider: %s (supported: openai, anthropic, google-antigravity)",
					req.Provider,
				),
				http.StatusBadRequest,
			)
		}
	})

	// POST /api/auth/logout — logout a provider
	mux.HandleFunc("POST /api/auth/logout", func(w http.ResponseWriter, r *http.Request) {
		var req struct {
			Provider string `json:"provider"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}

		if req.Provider == "" {
			if err := auth.DeleteAllCredentials(); err != nil {
				http.Error(w, fmt.Sprintf("Failed to logout: %v", err), http.StatusInternalServerError)
				return
			}
			clearAllAuthMethodsInConfig(absPath)
		} else {
			if err := auth.DeleteCredential(req.Provider); err != nil {
				http.Error(w, fmt.Sprintf("Failed to logout: %v", err), http.StatusInternalServerError)
				return
			}
			clearAuthMethodInConfig(absPath, req.Provider)
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	// GET /auth/callback — OAuth browser callback for Google Antigravity
	mux.HandleFunc("GET /auth/callback", handleOAuthCallback)
}
