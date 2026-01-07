package services

import "context"

type GitHubUser struct {
	ID    int64  `json:"id"`
	Email string `json:"email"`
	Login string `json:"login"`
}

type GitHubServiceInterface interface {
	ExchangeCode(ctx context.Context, code string) (string, error)
	GetUser(ctx context.Context, accessToken string) (*GitHubUser, error)
}
