package login

import (
	"errors"
	"sync"
	"time"
)

var ErrNotFound = errors.New("login token not found")
var ErrExpired = errors.New("login token expired")

type Store struct {
	mu     sync.Mutex
	tokens map[string]*LoginToken
	ttl    time.Duration
}

func NewStore(ttl time.Duration) *Store {
	return &Store{
		tokens: make(map[string]*LoginToken),
		ttl:    ttl,
	}
}
