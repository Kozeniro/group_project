package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func ProfileHandler(c *gin.Context) {
	userID := c.GetString("userID")

	roles, _ := c.Get("roles")
	permissions, _ := c.Get("permissions")

	c.JSON(http.StatusOK, gin.H{
		"user_id":     userID,
		"roles":       roles,
		"permissions": permissions,
	})
}
