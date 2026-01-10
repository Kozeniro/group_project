package handlers

import (
	"net/http"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type YandexCallbackHandler struct {
	yandexService *services.YandexService
	authService   *services.AuthService
	codeService   *services.CodeService
}

func NewYandexCallbackHandler(
	yandex *services.YandexService,
	auth *services.AuthService,
	code *services.CodeService,
) *YandexCallbackHandler {
	return &YandexCallbackHandler{
		yandexService: yandex,
		authService:   auth,
		codeService:   code,
	}
}

func (h *YandexCallbackHandler) Callback(c *gin.Context) {
	// 1. OAuth code от Яндекса
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no code"})
		return
	}

	// 2. login_token (передавали в state)
	loginToken := c.Query("state")
	if loginToken == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "no login token"})
		return
	}

	// 3. exchange code -> Yandex access token
	accessToken, err := h.yandexService.ExchangeCode(
		c.Request.Context(),
		code,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 4. get Yandex user
	user, err := h.yandexService.GetUser(
		c.Request.Context(),
		accessToken,
	)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	// 5. создаём 6-значный login code
	loginCode := h.codeService.CreateCode(loginToken)

	// 6. JWT НЕ выдаём — только code
	c.JSON(http.StatusOK, gin.H{
		"message":    "enter this code to finish login",
		"code":       loginCode,
		"expires_in": 60,
		"yandex_id":  user.ID,    // можно убрать позже
		"email":      user.Email, // можно убрать позже
	})
}
