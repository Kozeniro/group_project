package services

import "context"

type RefreshStore interface {
	Save(ctx context.Context, userID string, token string) error
	Exists(ctx context.Context, userID string, token string) (bool, error)
	Delete(ctx context.Context, userID string) error
}
