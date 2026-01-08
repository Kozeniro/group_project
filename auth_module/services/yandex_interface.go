package services

import "context"

type YandexUser struct {
	ID    string `json:"id"`
	Email string `json:"default_email"`
}
type YandexServiceInterface interface {
	ExchangeCode(ctx context.Context, code string) (string, error)
	GetUser(ctx context.Context, accessToken string) (*YandexUser, error)
}
