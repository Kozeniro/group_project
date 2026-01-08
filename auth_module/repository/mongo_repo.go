package repository

import (
	"context"
	"time"

	"github.com/adziasanovablamet/auth-module/models"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type MongoUserRepository struct {
	collection *mongo.Collection
}

func NewMongoUserRepository(db *mongo.Database) *MongoUserRepository {
	return &MongoUserRepository{
		collection: db.Collection("users"),
	}
}

func (r *MongoUserRepository) Create(ctx context.Context, user *models.User) error {
	user.CreatedAt = time.Now()

	_, err := r.collection.InsertOne(ctx, user)
	return err
}

func (r *MongoUserRepository) FindByEmail(ctx context.Context, email string) (*models.User, error) {
	var user models.User

	err := r.collection.FindOne(ctx, bson.M{"email": email}).Decode(&user)
	if err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *MongoUserRepository) FindByID(ctx context.Context, id string) (*models.User, error) {
	var user models.User

	err := r.collection.FindOne(ctx, bson.M{"_id": id}).Decode(&user)
	if err != nil {
		return nil, err
	}

	return &user, nil
}
func (r *MongoUserRepository) FindByGitHubID(ctx context.Context, githubID int64) (*models.User, error) {
	var user models.User

	err := r.collection.FindOne(ctx, bson.M{
		"github_id": githubID,
		"provider":  "github",
	}).Decode(&user)

	if err == mongo.ErrNoDocuments {
		return nil, ErrNotFound
	}

	return &user, err
}
