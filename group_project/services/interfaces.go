package services

import (
	"context"
)

type AuthServiceInterface interface {
	LoginWithGitHub(
		ctx context.Context,
		githubID int64,
		email string,
	) (*AuthResult, error)
}
