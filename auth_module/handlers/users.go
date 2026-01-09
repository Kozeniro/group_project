package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func CreateUserHandler(c *gin.Context) {
	c.JSON(http.StatusCreated, gin.H{
		"message": "user created (stub)",
	})
}
