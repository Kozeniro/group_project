package login

import (
	"time"

	"github.com/google/uuid"
)

func (s *Store) Create() *LoginToken {
	s.mu.Lock()
	defer s.mu.Unlock()

	token := uuid.NewString()

	lt := &LoginToken{
		Token:     token,
		ExpiresAt: time.Now().Add(s.ttl),
		Status:    StatusPending,
	}

	s.tokens[token] = lt
	return lt
}
