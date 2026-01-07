package repository

import (
	"context"
	"errors"

	"github.com/adziasanovablamet/auth-module/models"
)

var ErrNotFound = errors.New("not found")

type UserRepository interface {
	Create(ctx context.Context, user *models.User) error
	FindByEmail(ctx context.Context, email string) (*models.User, error)
	FindByID(ctx context.Context, id string) (*models.User, error)
	FindByGitHubID(ctx context.Context, githubID int64) (*models.User, error)
}
