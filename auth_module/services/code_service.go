package services

import (
	"errors"
	"fmt"
	"math/rand"
	"sync"
	"time"
)

type CodeEntry struct {
	LoginToken string
	ExpiresAt  time.Time
}

type CodeService struct {
	mu    sync.Mutex
	codes map[string]CodeEntry
}

func NewCodeService() *CodeService {
	return &CodeService{
		codes: make(map[string]CodeEntry),
	}
}

func generateCode() string {
	rand.Seed(time.Now().UnixNano())
	return fmt.Sprintf("%06d", rand.Intn(1000000))
}

// Создаёт одноразовый код (6 цифр) для login token
func (s *CodeService) CreateCode(loginToken string) string {
	s.mu.Lock()
	defer s.mu.Unlock()

	code := generateCode()

	s.codes[code] = CodeEntry{
		LoginToken: loginToken,
		ExpiresAt:  time.Now().Add(1 * time.Minute),
	}

	return code
}

// Проверяет код и возвращает login token
func (s *CodeService) VerifyCode(code string) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	entry, ok := s.codes[code]
	if !ok {
		return "", errors.New("code not found")
	}

	if time.Now().After(entry.ExpiresAt) {
		delete(s.codes, code)
		return "", errors.New("code expired")
	}

	delete(s.codes, code)
	return entry.LoginToken, nil
}
