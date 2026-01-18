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
	codeService := services.NewCodeService()

	// ===== Auth Service =====
	authService := services.NewAuthService(
		jwtService,
		refreshStore,
		userRepo,
		codeService,
	)
	githubService := services.NewGitHubService(
		cfg.GitHubClientID,
		cfg.GitHubClientSecret,
		cfg.GitHubRedirectURL,
	)
	yandexService := services.NewYandexService(
		cfg.YandexClientID,
		cfg.YandexClientSecret,
		cfg.YandexRedirectURL,
	)
	// ===== Handlers =====
	authHandler := handlers.NewAuthHandler(authService)
	sessionService := services.NewSessionService(24 * time.Hour)
	loginStatusHandler := handlers.NewLoginStatusHandler(
		loginStore,
		codeService,
		authService,
		sessionService,
	)

	// ===== Middleware =====
	authMiddleware := middleware.NewAuthMiddleware(jwtService)

	// ===== Router =====
	r := gin.Default()
	r.GET("/profile",
		authMiddleware.RequireAuth(),
		handlers.ProfileHandler,
	)

	r.GET("/admin",
		authMiddleware.RequireAuth(),
		authMiddleware.RequireRole("admin"),
		handlers.AdminHandler,
	)

	adminHandler := handlers.NewAdminHandler(authService)

	r.POST("/users/:id/roles",
		authMiddleware.RequireAuth(),
		adminHandler.SetUserRoles,
	)

	tokenHandler := handlers.NewTokenHandler(
		loginStore,
		codeService,
		authService,
		jwtService,
	)
	githubCallbackHandler := handlers.NewGitHubCallbackHandler(
		githubService,
		authService,
		codeService,
		loginStore,
	)
	yandexCallbackHandler := handlers.NewYandexCallbackHandler(
		yandexService,
		authService,
		codeService,
		loginStore,
	)
	CodeLoginHandler := handlers.NewCodeLoginHandler(
		codeService,
	)
	// ===== Auth routes =====
	auth := r.Group("/auth")
	{
		auth.POST("/login/token", tokenHandler.CreateLoginToken)
		auth.GET("/login/github", tokenHandler.GitHubLogin)
		auth.GET("/github/callback", githubCallbackHandler.Callback)
		auth.GET("/login/yandex", tokenHandler.YandexLogin)
		auth.GET("/yandex/callback", yandexCallbackHandler.Callback)
		auth.POST("/login", authHandler.Login)
		auth.POST("/register", authHandler.Register)
		auth.POST("/refresh", authHandler.Refresh)
		auth.POST("/logout", authHandler.Logout)

		// 🔹 Проверка статуса login_token
		auth.GET("/status", loginStatusHandler.Status)
		auth.GET("login/code", CodeLoginHandler.Start)
		auth.POST("login/code/verify", tokenHandler.Verify)
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
