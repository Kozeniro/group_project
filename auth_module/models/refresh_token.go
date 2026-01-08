package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type RefreshToken struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	Token     string             `bson:"token"`
	UserID    string             `bson:"user_id"`
	ExpiresAt time.Time          `bson:"expires_at"`
	CreatedAt time.Time          `bson:"created_at"`
}
