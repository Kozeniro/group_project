package services

import "errors"

var (
	ErrInvalidCredentials   = errors.New("invalid credentials")
	ErrInvalidRefreshToken  = errors.New("invalid refresh token")
	ErrRefreshTokenNotFound = errors.New("refresh token not found")
	ErrUserAlreadyExists    = errors.New("user already exists")
)
