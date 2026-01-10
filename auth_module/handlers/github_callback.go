package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type GitHubCallbackHandler struct {
	githubService *services.GitHubService
	authService   *services.AuthService
	codeService   *services.CodeService
}

func NewGitHubCallbackHandler(
	github *services.GitHubService,
	auth *services.AuthService,
	code *services.CodeService,
) *GitHubCallbackHandler {
	return &GitHubCallbackHandler{
		githubService: github,
		authService:   auth,
		codeService:   code,
	}
}
func (h *GitHubCallbackHandler) Callback(c *gin.Context) {
	// 1. OAuth code от GitHub
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no code"})
		return
	}

	// 2. login_token (мы передавали его в state)
	loginToken := c.Query("state")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no login token"})
		return
	}

	// 3. exchange code -> GitHub access token
	accessToken, err := h.githubService.ExchangeCode(
		c.Request.Context(),
		code,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 4. get GitHub user
	user, err := h.githubService.GetUser(
		c.Request.Context(),
		accessToken,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 5. создаём 6-значный login code (code authentication)
	loginCode := h.codeService.CreateCode(loginToken)

	// 6. ВАЖНО: JWT НЕ выдаём здесь
	c.JSON(http.StatusOK, gin.H{
		"message":    "enter this code to finish login",
		"code":       loginCode,
		"expires_in": 60,
		"github_id":  user.ID,    // можно оставить для дебага
		"email":      user.Email, // можно убрать позже
	})
}
