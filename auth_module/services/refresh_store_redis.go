package services

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisRefreshStore struct {
	client *redis.Client
}

func NewRedisRefreshStore(addr, password string, db int) RefreshStore {
	rdb := redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: password,
		DB:       db,
	})

	return &RedisRefreshStore{
		client: rdb,
	}
}

func (r *RedisRefreshStore) Save(
	ctx context.Context,
	userID string,
	token string,
) error {
	return r.client.Set(ctx, userID, token, 7*24*time.Hour).Err()
}

func (r *RedisRefreshStore) Exists(
	ctx context.Context,
	userID string,
	token string,
) (bool, error) {
	val, err := r.client.Get(ctx, userID).Result()
	if err == redis.Nil {
		return false, ErrRefreshTokenNotFound
	}
	if err != nil {
		return false, err
	}
	return val == token, nil
}

func (r *RedisRefreshStore) Delete(
	ctx context.Context,
	userID string,
) error {
	return r.client.Del(ctx, userID).Err()
}
