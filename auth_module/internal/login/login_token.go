package login

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type Status string

const (
	StatusPending  Status = "pending"
	StatusApproved Status = "approved"
	StatusDenied   Status = "denied"
	StatusExpired  Status = "expired"
)

type LoginToken struct {
	Token     string
	ExpiresAt time.Time
	Status    Status
	UserID    primitive.ObjectID

	AccessToken  string
	RefreshToken string
}
