package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type ChangeMyRoleHandler struct {
	authService *services.AuthService
}

func NewChangeMyRoleHandler(authService *services.AuthService) *ChangeMyRoleHandler {
	return &ChangeMyRoleHandler{
		authService: authService,
	}
}

type changeRoleRequest struct {
	Role string `json:"role"`
}

func (h *ChangeMyRoleHandler) Handle(c *gin.Context) {
	userIDAny, ok := c.Get("userID")
	if !ok {
		c.AbortWithStatus(http.StatusUnauthorized)
		return
	}

	userID := userIDAny.(string)

	var req changeRoleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid body"})
		return
	}

	if err := h.authService.ChangeMyRole(
		c.Request.Context(),
		userID,
		req.Role,
	); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusNoContent)
}
