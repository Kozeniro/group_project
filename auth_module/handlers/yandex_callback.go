package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type YandexCallbackHandler struct {
	yandexService *services.YandexService
	authService   *services.AuthService
}

func NewYandexCallbackHandler(
	yandex *services.YandexService,
	auth *services.AuthService,
) *YandexCallbackHandler {
	return &YandexCallbackHandler{
		yandexService: yandex,
		authService:   auth,
	}
}

func (h *YandexCallbackHandler) Callback(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no code"})
		return
	}

	// 1. exchange code → access token
	accessToken, err := h.yandexService.ExchangeCode(
		c.Request.Context(),
		code,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 2. get yandex user
	user, err := h.yandexService.GetUser(
		c.Request.Context(),
		accessToken,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 3. login / register
	tokens, err := h.authService.LoginWithYandex(
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
