package login

import "time"

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

	AccessToken  string
	RefreshToken string
}
