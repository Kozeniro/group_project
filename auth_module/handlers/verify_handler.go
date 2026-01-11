package handlers

import (
	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/adziasanovablamet/auth-module/services"
)

type VerifyHandler struct {
	codeService *services.CodeService
	loginStore  *login.Store
	authService *services.AuthService
}

func NewVerifyHandler(
	codeService *services.CodeService,
	loginStore *login.Store,
	authService *services.AuthService,
) *VerifyHandler {
	return &VerifyHandler{
		codeService: codeService,
		loginStore:  loginStore,
		authService: authService,
	}
}
