package repository

import (
	"context"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func EnsureMongoIndexes(ctx context.Context, db *mongo.Database) error {
	// ===== USERS =====
	users := db.Collection("users")

	_, err := users.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys: bson.D{
			{Key: "email", Value: 1},
		},
		Options: options.Index().SetUnique(true),
	})
	if err != nil {
		return err
	}

	// ===== REFRESH TOKENS =====
	refreshTokens := db.Collection("refresh_tokens")

	// unique token
	_, err = refreshTokens.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys: bson.D{
			{Key: "token", Value: 1},
		},
		Options: options.Index().SetUnique(true),
	})
	if err != nil {
		return err
	}

	// TTL index
	_, err = refreshTokens.Indexes().CreateOne(ctx, mongo.IndexModel{
		Keys: bson.D{
			{Key: "expires_at", Value: 1},
		},
		Options: options.Index().
			SetExpireAfterSeconds(0),
	})
	if err != nil {
		return err
	}

	return nil
}
