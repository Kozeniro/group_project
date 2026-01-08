package login

import "time"

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
