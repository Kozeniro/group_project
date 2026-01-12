package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type GitHubCallbackHandler struct {
	githubService *services.GitHubService
	authService   *services.AuthService
	codeService   *services.CodeService
	store         *login.Store
}

func NewGitHubCallbackHandler(
	github *services.GitHubService,
	auth *services.AuthService,
	code *services.CodeService,
	store *login.Store,
) *GitHubCallbackHandler {
	return &GitHubCallbackHandler{
		githubService: github,
		authService:   auth,
		codeService:   code,
		store:         store,
	}
}
func (h *GitHubCallbackHandler) Callback(c *gin.Context) {
	// 1. OAuth code от GitHub
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no code"})
		return
	}

	// 2. login_token (state)
	loginToken := c.Query("state")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no login token"})
		return
	}

	// 3. exchange code -> GitHub access token
	ghAccessToken, err := h.githubService.ExchangeCode(
		c.Request.Context(),
		code,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 4. get GitHub user
	guser, err := h.githubService.GetUser(
		c.Request.Context(),
		ghAccessToken,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 5. login / register user
	user, err := h.authService.LoginWithGitHub(
		c.Request.Context(),
		guser.ID,
		guser.Email,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	h.store.AttachUser(loginToken, user.User.ID)
	// 8. ответ клиенту (Web / Telegram)
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"github_id": guser.ID,
		"email":     guser.Email,
	})
}
