package handlers

import (
	"net/http"
	"net/url"
	"os"

	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/gin-gonic/gin"
)

type TokenHandler struct {
	Store *login.Store
}

func NewTokenHandler(store *login.Store) *TokenHandler {
	return &TokenHandler{Store: store}
}

// POST /auth/login/token
func (h *TokenHandler) CreateLoginToken(c *gin.Context) {
	lt := h.Store.Create()

	c.JSON(http.StatusOK, gin.H{
		"login_token": lt.Token,
		"expires_at":  lt.ExpiresAt,
	})
}

// GET /auth/login/github?token=...
func (h *TokenHandler) GitHubLogin(c *gin.Context) {
	loginToken := c.Query("token")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "token is required"})
		return
	}

	// проверка login token
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
func (h *TokenHandler) YandexLogin(c *gin.Context) {
	loginToken := c.Query("token")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "token is required"})
		return
	}

	// проверка login token
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
