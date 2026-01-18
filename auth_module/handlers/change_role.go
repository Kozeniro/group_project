package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type SetUserRolesRequest struct {
	Roles []string `json:"roles"`
}
type Adminhandler struct {
	authService *services.AuthService
}

func NewAdminHandler(authService *services.AuthService) *Adminhandler {
	return &Adminhandler{authService: authService}
}
func (h *Adminhandler) SetUserRoles(c *gin.Context) {
	targetUserID := c.Param("id")

	var req SetUserRolesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid body"})
		return
	}

	if err := h.authService.SetUserRoles(
		c.Request.Context(),
		targetUserID,
		req.Roles,
	); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusNoContent)
}
func (h *Adminhandler) UserPermissions(c *gin.Context) {
	targetUserID := c.Param("id")

	roles, permissions, err := h.authService.GetUserRolesAndPermissions(
		c.Request.Context(),
		targetUserID,
	)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user_id":     targetUserID,
		"roles":       roles,
		"permissions": permissions,
	})
}
