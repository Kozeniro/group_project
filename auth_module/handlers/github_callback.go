package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type GitHubCallbackHandler struct {
	githubService *services.GitHubService
	authService   *services.AuthService
}

func NewGitHubCallbackHandler(
	github *services.GitHubService,
	auth *services.AuthService,
) *GitHubCallbackHandler {
	return &GitHubCallbackHandler{
		githubService: github,
		authService:   auth,
	}
}
func (h *GitHubCallbackHandler) Callback(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no code"})
		return
	}

	// 1. exchange code → access token
	accessToken, err := h.githubService.ExchangeCode(
		c.Request.Context(),
		code,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 2. get github user
	user, err := h.githubService.GetUser(
		c.Request.Context(),
		accessToken,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 3. login / register
	tokens, err := h.authService.LoginWithGitHub(
		c.Request.Context(),
		user.ID,
		user.Email,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 4. SUCCESS
	c.JSON(http.StatusOK, tokens)
}
