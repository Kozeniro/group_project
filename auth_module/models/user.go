package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
	"golang.org/x/crypto/bcrypt"
)

type User struct {
	ID       primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	Email    string             `bson:"email" json:"email"`
	Password string             `bson:"password,omitempty" json:"-"`
	Provider string             `bson:"provider" json:"provider"` // local / github / yandex

	GitHubID int64  `bson:"github_id,omitempty" json:"github_id,omitempty"`
	YandexID string `bson:"yandex_id,omitempty" json:"yandex_id,omitempty"`

	Roles []string `bson:"roles" json:"roles"`

	CreatedAt time.Time `bson:"created_at" json:"created_at"`
}

func (u *User) CheckPassword(password string) bool {
	return bcrypt.CompareHashAndPassword(
		[]byte(u.Password),
		[]byte(password),
	) == nil
}
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}
