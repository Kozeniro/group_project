package services

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
	"golang.org/x/crypto/bcrypt"

	"github.com/adziasanovablamet/auth-module/models"
	"github.com/adziasanovablamet/auth-module/repository"
)

type AuthService struct {
	jwtService   *JWTService
	refreshStore RefreshStore
	userRepo     repository.UserRepository
}

type AuthResult struct {
	User         *models.User
	AccessToken  string
	RefreshToken string
}

func NewAuthService(
	jwt *JWTService,
	refreshStore RefreshStore,
	userRepo repository.UserRepository,
) *AuthService {
	return &AuthService{
		jwtService:   jwt,
		refreshStore: refreshStore,
		userRepo:     userRepo,
	}
}

/* ========= REGISTER ========= */

func (s *AuthService) Register(
	ctx context.Context,
	email string,
	password string,
) error {

	_, err := s.userRepo.FindByEmail(ctx, email)
	if err == nil {
		return ErrUserAlreadyExists
	}

	hashedPassword, err := bcrypt.GenerateFromPassword(
		[]byte(password),
		bcrypt.DefaultCost,
	)
	if err != nil {
		return err
	}

	user := &models.User{
		Email:     email,
		Password:  string(hashedPassword),
		Provider:  "local",
		CreatedAt: time.Now(),
	}

	return s.userRepo.Create(ctx, user)
}

/* ========= LOGIN ========= */

func (s *AuthService) Login(
	ctx context.Context,
	email string,
	password string,
) (string, string, error) {

	user, err := s.userRepo.FindByEmail(ctx, email)
	if err != nil {
		return "", "", ErrInvalidCredentials
	}

	if err := bcrypt.CompareHashAndPassword(
		[]byte(user.Password),
		[]byte(password),
	); err != nil {
		return "", "", ErrInvalidCredentials
	}

	userID := user.ID.Hex()

	accessToken, err := s.jwtService.GenerateAccessToken(userID)
	if err != nil {
		return "", "", err
	}

	refreshToken, err := s.jwtService.GenerateRefreshToken(userID)
	if err != nil {
		return "", "", err
	}

	if err := s.refreshStore.Save(ctx, userID, refreshToken); err != nil {
		return "", "", err
	}

	return accessToken, refreshToken, nil
}

/* ========= REFRESH ========= */

func (s *AuthService) Refresh(
	ctx context.Context,
	refreshToken string,
) (string, string, error) {

	claims, err := s.jwtService.ValidateRefreshToken(refreshToken)
	if err != nil {
		return "", "", ErrInvalidRefreshToken
	}

	exists, err := s.refreshStore.Exists(ctx, claims.UserID, refreshToken)
	if err != nil || !exists {
		return "", "", ErrInvalidRefreshToken
	}

	accessToken, err := s.jwtService.GenerateAccessToken(claims.UserID)
	if err != nil {
		return "", "", err
	}

	newRefreshToken, err := s.jwtService.GenerateRefreshToken(claims.UserID)
	if err != nil {
		return "", "", err
	}

	_ = s.refreshStore.Delete(ctx, claims.UserID)
	_ = s.refreshStore.Save(ctx, claims.UserID, newRefreshToken)

	return accessToken, newRefreshToken, nil
}

/* ========= LOGOUT ========= */

func (s *AuthService) Logout(
	ctx context.Context,
	userID string,
) error {
	return s.refreshStore.Delete(ctx, userID)
}

/* ========= GITHUB LOGIN ========= */

func (s *AuthService) LoginWithGitHub(
	ctx context.Context,
	githubID int64,
	email string,
) (*AuthResult, error) {

	user, err := s.userRepo.FindByGitHubID(ctx, githubID)

	if err == repository.ErrNotFound {
		user = &models.User{
			ID:        primitive.NewObjectID(),
			Email:     email,
			Provider:  "github",
			GitHubID:  githubID,
			CreatedAt: time.Now(),
		}

		if err := s.userRepo.Create(ctx, user); err != nil {
			return nil, err
		}
	} else if err != nil {
		return nil, err
	}

	userID := user.ID.Hex()

	accessToken, err := s.jwtService.GenerateAccessToken(userID)
	if err != nil {
		return nil, err
	}

	refreshToken, err := s.jwtService.GenerateRefreshToken(userID)
	if err != nil {
		return nil, err
	}

	return &AuthResult{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		User:         user,
	}, nil
}
