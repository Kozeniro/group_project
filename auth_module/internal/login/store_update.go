package login

func (s *Store) Approve(token, access, refresh string) error {
	lt, err := s.Get(token)
	if err != nil {
		return err
	}

	lt.Status = StatusApproved
	lt.AccessToken = access
	lt.RefreshToken = refresh
	return nil
}

func (s *Store) Deny(token string) error {
	lt, err := s.Get(token)
	if err != nil {
		return err
	}

	lt.Status = StatusDenied
	return nil
}
func (s *Store) Update(lt *LoginToken) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.tokens[lt.Token]; !ok {
		return ErrNotFound
	}

	s.tokens[lt.Token] = lt
	return nil
}
