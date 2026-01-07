package main

import (
	"log"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/adziasanovablamet/auth-module/config"
	"github.com/adziasanovablamet/auth-module/handlers"
	"github.com/adziasanovablamet/auth-module/internal/login"
	"github.com/adziasanovablamet/auth-module/middleware"
	"github.com/adziasanovablamet/auth-module/repository"
	"github.com/adziasanovablamet/auth-module/services"
)

func main() {
	// ===== config =====
	cfg := config.Load()

	// ===== MongoDB =====
	mongoClient, err := repository.NewMongoClient(cfg.MongoURI)
	if err != nil {
		log.Fatal(err)
	}
	db := mongoClient.Database(cfg.MongoDB)

	userRepo := repository.NewMongoUserRepository(db)

	// ===== Redis (refresh tokens) =====
	refreshStore := services.NewRedisRefreshStore(
		cfg.RedisAddr,
		cfg.RedisPassword,
		cfg.RedisDB,
	)

	// ===== JWT =====
	jwtService := services.NewJWTService(
		cfg.JWTAccessSecret,
		cfg.JWTRefreshSecret,
	)

	// ===== Login Token Store (state / token входа) =====
	// Живёт ТОЛЬКО в модуле авторизации
	loginStore := login.NewStore(5 * time.Minute)

	// ===== Auth Service =====
	authService := services.NewAuthService(
		jwtService,
		refreshStore,
		userRepo,
	)
	githubService := services.NewGitHubService(
		cfg.GitHubClientID,
		cfg.GitHubClientSecret,
		cfg.GitHubRedirectURL,
	)
	// ===== Handlers =====
	authHandler := handlers.NewAuthHandler(authService)
	loginStatusHandler := handlers.NewLoginStatusHandler(loginStore)

	// ===== Middleware =====
	authMiddleware := middleware.NewAuthMiddleware(jwtService)

	// ===== Router =====
	r := gin.Default()

	tokenHandler := handlers.NewTokenHandler(loginStore)
	githubCallbackHandler := handlers.NewGitHubCallbackHandler(
		githubService,
		authService,
	)
	// ===== Auth routes =====
	auth := r.Group("/auth")
	{
		auth.POST("/login/token", tokenHandler.CreateLoginToken)
		auth.GET("/login/github", tokenHandler.GitHubLogin)
		auth.GET("/github/callback", githubCallbackHandler.Callback)
		auth.POST("/login", authHandler.Login)
		auth.POST("/register", authHandler.Register)
		auth.POST("/refresh", authHandler.Refresh)
		auth.POST("/logout", authHandler.Logout)

		// 🔹 Проверка статуса login_token
		auth.GET("/status", loginStatusHandler.Status)
	}

	// ===== Protected routes =====
	protected := r.Group("/protected")
	protected.Use(authMiddleware.RequireAuth())
	{
		protected.GET("/me", authHandler.Me)
	}

	log.Println("Auth service started on :8081")
	r.Run(":8081")
}
