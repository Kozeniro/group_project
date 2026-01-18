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
	JwtService  *services.JWTService
}
type CodeLoginHandler struct {
	CodeService *services.CodeService
}
type CodeVerifyRequest struct {
	Code         string `json:"code"`
	RefreshToken string `json:"refresh_token"`
}

func NewCodeLoginHandler(
	codeService *services.CodeService,
) *CodeLoginHandler {
	return &CodeLoginHandler{
		CodeService: codeService,
	}
}
func (h *CodeLoginHandler) Start(c *gin.Context) {
	loginToken := c.Query("state")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no login token"})
		return
	}

	// создаём 6-значный код
	code := h.CodeService.CreateCode(loginToken)

	c.JSON(http.StatusOK, gin.H{
		"message":    "enter this code to finish login",
		"code":       code,
		"expires_in": 60,
	})
}
func NewTokenHandler(
	store *login.Store,
	codeService *services.CodeService,
	authService *services.AuthService,
	jwtService *services.JWTService,
) *TokenHandler {
	return &TokenHandler{
		Store:       store,
		CodeService: codeService,
		AuthService: authService,
		JwtService:  jwtService,
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
func (h *TokenHandler) Verify(c *gin.Context) {
	var req CodeVerifyRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 1. code -> loginToken
	loginToken, err := h.CodeService.VerifyCode(req.Code)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 2. проверить refresh token
	claims, err := h.JwtService.ValidateRefreshToken(req.RefreshToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid refresh token"})
		return
	}

	// 3. найти пользователя по email
	user, err := h.AuthService.UserRepo.FindByEmail(
		c.Request.Context(),
		claims.Email,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found"})
		return
	}

	// 4. привязать пользователя к login token
	if err := h.Store.AttachUser(loginToken, user.ID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 5. НИЧЕГО БОЛЬШЕ НЕ ДЕЛАЕМ
	c.JSON(http.StatusOK, gin.H{
		"status": "approved",
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
