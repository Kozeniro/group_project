package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/gin-gonic/gin"
)

type LoginStatusHandler struct {
	store *login.Store
}

func NewLoginStatusHandler(store *login.Store) *LoginStatusHandler {
	return &LoginStatusHandler{store: store}
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

	resp := gin.H{
		"status": lt.Status,
	}

	if lt.Status == login.StatusApproved {
		resp["access_token"] = lt.AccessToken
		resp["refresh_token"] = lt.RefreshToken
	}

	c.JSON(http.StatusOK, resp)
}
