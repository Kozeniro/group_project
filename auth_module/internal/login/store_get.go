package login

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

func (s *Store) Get(token string) (*LoginToken, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	lt, ok := s.tokens[token]
	if !ok {
		return nil, ErrNotFound
	}

	if time.Now().After(lt.ExpiresAt) {
		lt.Status = StatusExpired
		return nil, ErrExpired
	}

	return lt, nil
}
func (s *Store) AttachUser(token string, userID primitive.ObjectID) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	entry, ok := s.tokens[token]
	if !ok {
		return ErrNotFound
	}

	entry.UserID = userID
	s.tokens[token] = entry
	return nil
}
