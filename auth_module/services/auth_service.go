package services

import (
	"context"
	"errors"
	"time"

	"github.com/adziasanovablamet/auth-module/internal/auth"
	"github.com/adziasanovablamet/auth-module/models"
	"github.com/adziasanovablamet/auth-module/repository"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

type AuthResult struct {
	AccessToken  string       `json:"access_token"`
	RefreshToken string       `json:"refresh_token"`
	User         *models.User `json:"user"`
}

type AuthService struct {
	jwtService   *JWTService
	refreshStore RefreshStore
	UserRepo     repository.UserRepository
	codeService  *CodeService
}

func NewAuthService(
	jwt *JWTService,
	refreshStore RefreshStore,
	userRepo repository.UserRepository,
	codeService *CodeService,
) *AuthService {
	return &AuthService{
		jwtService:   jwt,
		refreshStore: refreshStore,
		UserRepo:     userRepo,
		codeService:  codeService,
	}
}

/////////////////////////////////////////////////////
// 🔐 REGISTER (email + password)
/////////////////////////////////////////////////////

func (s *AuthService) Register(
	ctx context.Context,
	email string,
	password string,
) (*AuthResult, error) {

	_, err := s.UserRepo.FindByEmail(ctx, email)
	if err == nil {
		return nil, errors.New("user already exists")
	}

	hashed, err := models.HashPassword(password)
	if err != nil {
		return nil, err
	}

	user := &models.User{
		ID:        primitive.NewObjectID(),
		Email:     email,
		Password:  hashed,
		Provider:  "local",
		Roles:     []string{"student"},
		CreatedAt: time.Now(),
	}

	if err := s.UserRepo.Create(ctx, user); err != nil {
		return nil, err
	}

	return s.IssueTokens(ctx, user)
}

/////////////////////////////////////////////////////
// 🔐 LOGIN (email + password)
/////////////////////////////////////////////////////

func (s *AuthService) Login(
	ctx context.Context,
	Email string,
	Password string,
) (*AuthResult, error) {

	user, err := s.UserRepo.FindByEmail(ctx, Email)
	if err != nil {
		return nil, err
	}

	if !user.CheckPassword(Password) {
		return nil, ErrInvalidCredentials
	}

	return s.IssueTokens(ctx, user)
}

/////////////////////////////////////////////////////
// 🔐 LOGIN WITH GITHUB
/////////////////////////////////////////////////////

func (s *AuthService) LoginWithGitHub(
	ctx context.Context,
	githubID int64,
	email string,
) (*AuthResult, error) {

	user, err := s.UserRepo.FindByGitHubID(ctx, githubID)

	if err == repository.ErrNotFound {
		user = &models.User{
			ID:        primitive.NewObjectID(),
			Email:     email,
			Provider:  "github",
			GitHubID:  githubID,
			Roles:     []string{"student"},
			CreatedAt: time.Now(),
		}

		if err := s.UserRepo.Create(ctx, user); err != nil {
			return nil, err
		}
	} else if err != nil {
		return nil, err
	}

	return s.IssueTokens(ctx, user)
}

/////////////////////////////////////////////////////
// 🔐 LOGIN WITH YANDEX (ВОТ ОН, ТВОЙ КУСОК)
/////////////////////////////////////////////////////

func (s *AuthService) LoginWithYandex(
	ctx context.Context,
	yandexID string,
	email string,
) (*AuthResult, error) {

	user, err := s.UserRepo.FindByYandexID(ctx, yandexID)

	if err == repository.ErrNotFound {
		user = &models.User{
			ID:        primitive.NewObjectID(),
			Email:     email,
			Provider:  "yandex",
			YandexID:  yandexID,
			Roles:     []string{"student"},
			CreatedAt: time.Now(),
		}

		if err := s.UserRepo.Create(ctx, user); err != nil {
			return nil, err
		}
	} else if err != nil {
		return nil, err
	}

	return s.IssueTokens(ctx, user)
}

/////////////////////////////////////////////////////
// 🔁 REFRESH
/////////////////////////////////////////////////////

func (s *AuthService) Refresh(
	ctx context.Context,
	RefreshToken string,
) (*AuthResult, error) {

	claims, err := s.jwtService.ValidateRefreshToken(RefreshToken)
	if err != nil {
		return nil, err
	}

	user, err := s.UserRepo.FindByID(ctx, claims.UserID)
	if err != nil {
		return nil, err
	}

	return s.IssueTokens(ctx, user)
}

/////////////////////////////////////////////////////
// 🚪 LOGOUT
/////////////////////////////////////////////////////
/////////////////////////////////////////////////////
// 🔑 ОБЩАЯ ВЫДАЧА ТОКЕНОВ
/////////////////////////////////////////////////////

func (s *AuthService) IssueTokens(
	_ context.Context,
	user *models.User,
) (*AuthResult, error) {

	userID := user.ID.Hex()
	roles := user.Roles
	permissions := auth.PermissionsForRoles(roles)
	accessToken, err := s.jwtService.GenerateAccessToken(userID, roles, permissions)
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
func (s *AuthService) ChangeMyRole(
	ctx context.Context,
	userID string,
	newRole string,
) error {

	if newRole != auth.RoleUser && newRole != auth.RoleTeacher {
		return errors.New("invalid role")
	}

	return s.UserRepo.UpdateRole(ctx, userID, newRole)
}
