package services

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"sync"
	"time"
)

type Session struct {
	UserID       string
	AccessToken  string
	RefreshToken string
	ExpiresAt    time.Time
}

type SessionService struct {
	mu       sync.Mutex
	sessions map[string]*Session
	ttl      time.Duration
}

func NewSessionService(ttl time.Duration) *SessionService {
	return &SessionService{
		sessions: make(map[string]*Session),
		ttl:      ttl,
	}
}

func (s *SessionService) CreateSession(
	ctx context.Context,
	userID string,
	accessToken string,
	refreshToken string,
) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	token := generateSessionToken()

	s.sessions[token] = &Session{
		UserID:       userID,
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresAt:    time.Now().Add(s.ttl),
	}

	return token, nil
}

func (s *SessionService) Get(token string) (*Session, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()

	session, ok := s.sessions[token]
	if !ok {
		return nil, false
	}

	if time.Now().After(session.ExpiresAt) {
		delete(s.sessions, token)
		return nil, false
	}

	return session, true
}

func (s *SessionService) Delete(token string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.sessions, token)
}

func generateSessionToken() string {
	b := make([]byte, 32)
	rand.Read(b)
	return hex.EncodeToString(b)
}
