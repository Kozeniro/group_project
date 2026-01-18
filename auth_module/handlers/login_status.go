package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type LoginStatusHandler struct {
	store          *login.Store
	CodeService    *services.CodeService
	AuthService    *services.AuthService
	SessionService *services.SessionService
}

func NewLoginStatusHandler(store *login.Store,
	codeService *services.CodeService,
	authService *services.AuthService,
	sessionService *services.SessionService,
) *LoginStatusHandler {
	return &LoginStatusHandler{
		store:          store,
		CodeService:    codeService,
		AuthService:    authService,
		SessionService: sessionService,
	}
}

func (h *LoginStatusHandler) Status(c *gin.Context) {
	token := c.Query("login_token")
	if token == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "login_token required"})
		return
	}

	lt, err := h.store.Get(token)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"status": "expired"})
		return
	}
	var sessionToken string
	// 🔥 ФИНАЛИЗАЦИЯ ЛОГИНА
	if lt.Status == login.StatusPending && !lt.UserID.IsZero() {
		user, err := h.AuthService.UserRepo.FindByID(
			c.Request.Context(),
			lt.UserID.Hex(),
		)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found"})
			return
		}

		tokens, err := h.AuthService.IssueTokens(
			c.Request.Context(),
			user,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		sessionToken, err = h.SessionService.CreateSession(
			c.Request.Context(),
			user.ID.Hex(),
			tokens.AccessToken,
			tokens.RefreshToken,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		lt.Status = login.StatusApproved
		lt.AccessToken = tokens.AccessToken
		lt.RefreshToken = tokens.RefreshToken

		h.store.Update(lt)
	}

	resp := gin.H{
		"status": lt.Status,
	}

	if lt.Status == login.StatusApproved {
		resp["access_token"] = lt.AccessToken
		resp["refresh_token"] = lt.RefreshToken
		resp["session_token"] = sessionToken
	}

	c.JSON(http.StatusOK, resp)
}
