package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func AdminHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "admin access granted",
	})
}
