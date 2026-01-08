package services

import (
	"context"
	"time"

	"github.com/adziasanovablamet/auth-module/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type MongoRefreshStore struct {
	collection *mongo.Collection
}

func NewMongoRefreshStore(db *mongo.Database) *MongoRefreshStore {
	return &MongoRefreshStore{
		collection: db.Collection("refresh_tokens"),
	}
}

func (s *MongoRefreshStore) Save(token, userID string, ttl time.Duration) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	rt := models.RefreshToken{
		Token:     token,
		UserID:    userID,
		ExpiresAt: time.Now().Add(ttl),
		CreatedAt: time.Now(),
	}

	_, err := s.collection.InsertOne(ctx, rt)
	return err
}

func (s *MongoRefreshStore) Get(token string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var rt models.RefreshToken
	err := s.collection.FindOne(ctx, bson.M{"token": token}).Decode(&rt)
	if err != nil {
		return "", err
	}

	if time.Now().After(rt.ExpiresAt) {
		_ = s.Delete(token)
		return "", mongo.ErrNoDocuments
	}

	return rt.UserID, nil
}

func (s *MongoRefreshStore) Delete(token string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := s.collection.DeleteOne(ctx, bson.M{"token": token})
	return err
}
