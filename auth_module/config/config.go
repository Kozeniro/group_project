package config

import (
	"log"
	"os"
	"strconv"
)

type Config struct {
	// Server
	Port string

	// JWT
	JWTAccessSecret  string
	JWTRefreshSecret string

	// Redis
	RedisAddr     string
	RedisPassword string
	RedisDB       int

	// Mongo
	MongoURI string
	MongoDB  string

	//github
	GitHubClientID     string
	GitHubClientSecret string
	GitHubRedirectURL  string

	//yandex
	YandexClientID     string
	YandexClientSecret string
	YandexRedirectURL  string
}

func Load() *Config {
	redisDB, err := strconv.Atoi(getEnv("REDIS_DB", "0"))
	if err != nil {
		log.Fatal("REDIS_DB must be a number")
	}

	return &Config{
		// Server
		Port: getEnv("PORT", "8081"),

		// JWT
		JWTAccessSecret:  getEnv("JWT_ACCESS_SECRET", "access-secret"),
		JWTRefreshSecret: getEnv("JWT_REFRESH_SECRET", "refresh-secret"),

		// Redis
		RedisAddr:     getEnv("REDIS_ADDR", "localhost:6379"),
		RedisPassword: getEnv("REDIS_PASSWORD", ""),
		RedisDB:       redisDB,

		// Mongo ✅ ВОТ ОНИ
		MongoURI: getEnv("MONGO_URI", ""),
		MongoDB:  getEnv("MONGO_DB", "authdb"),

		//github
		GitHubClientID:     os.Getenv("GITHUB_CLIENT_ID"),
		GitHubClientSecret: os.Getenv("GITHUB_CLIENT_SECRET"),
		GitHubRedirectURL:  os.Getenv("GITHUB_REDIRECT_URL"),

		//yandex
		YandexClientID:     os.Getenv("YANDEX_CLIENT_ID"),
		YandexClientSecret: os.Getenv("YANDEX_CLIENT_SECRET"),
		YandexRedirectURL:  os.Getenv("YANDEX_REDIRECT_URL"),
	}
}

func getEnv(key, defaultValue string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return defaultValue
}
