package handlers

import (
	"net/http"
	"net/url"
	"os"

	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type TokenHandler struct {
	Store       *login.Store
	CodeService *services.CodeService
	AuthService *services.AuthService
}

func NewTokenHandler(
	store *login.Store,
	codeService *services.CodeService,
	authService *services.AuthService,
) *TokenHandler {
	return &TokenHandler{
		Store:       store,
		CodeService: codeService,
		AuthService: authService,
	}
}

// POST /auth/login/token
func (h *TokenHandler) CreateLoginToken(c *gin.Context) {
	lt := h.Store.Create()

	c.JSON(http.StatusOK, gin.H{
		"login_token": lt.Token,
		"expires_at":  lt.ExpiresAt,
	})
}

// POST /auth/login/code/verify
func (h *VerifyHandler) Verify(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "code required"})
		return
	}

	// 1. code -> loginToken
	loginToken, err := h.codeService.VerifyCode(code)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 2. loginToken -> login entry
	entry, err := h.loginStore.Get(loginToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}
	user, err := h.authService.UserRepo.FindByID(
		c.Request.Context(),
		entry.UserID.Hex(),
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found"})
	}
	// 3. выдаём JWT
	tokens, err := h.authService.IssueTokens(
		c.Request.Context(),
		user,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 4. одноразовый loginToken — удаляем

	c.JSON(http.StatusOK, gin.H{
		"access_token":  tokens.AccessToken,
		"refresh_token": tokens.RefreshToken,
	})
}

// GET /auth/login/github?token=...
func (h *TokenHandler) GitHubLogin(c *gin.Context) {
	loginToken := c.Query("token")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "token is required"})
		return
	}

	_, err := h.Store.Get(loginToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid login token"})
		return
	}

	q := url.Values{}
	q.Set("client_id", os.Getenv("GITHUB_CLIENT_ID"))
	q.Set("redirect_uri", os.Getenv("GITHUB_REDIRECT_URL"))
	q.Set("scope", "user:email")
	q.Set("state", loginToken)

	githubURL := "https://github.com/login/oauth/authorize?" + q.Encode()
	c.Redirect(http.StatusFound, githubURL)
}

// GET /auth/login/yandex?token=...
func (h *TokenHandler) YandexLogin(c *gin.Context) {
	loginToken := c.Query("token")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "token is required"})
		return
	}

	_, err := h.Store.Get(loginToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid login token"})
		return
	}

	q := url.Values{}
	q.Set("response_type", "code")
	q.Set("client_id", os.Getenv("YANDEX_CLIENT_ID"))
	q.Set("redirect_uri", os.Getenv("YANDEX_REDIRECT_URL"))
	q.Set("state", loginToken)

	yandexURL := "https://oauth.yandex.ru/authorize?" + q.Encode()
	c.Redirect(http.StatusFound, yandexURL)
}
