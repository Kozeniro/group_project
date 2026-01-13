package middleware

import (
	"net/http"
	"strings"

	"github.com/adziasanovablamet/auth-module/services"
	"github.com/gin-gonic/gin"
)

type AuthMiddleware struct {
	jwt *services.JWTService
}

func NewAuthMiddleware(jwt *services.JWTService) *AuthMiddleware {
	return &AuthMiddleware{jwt: jwt}
}

func (m *AuthMiddleware) RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatus(http.StatusUnauthorized)
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.AbortWithStatus(http.StatusUnauthorized)
			return
		}

		claims, err := m.jwt.ValidateAccessToken(parts[1])
		if err != nil {
			c.AbortWithStatus(http.StatusUnauthorized)
			return
		}

		c.Set("userID", claims.UserID)
		c.Set("roles", claims.Roles)
		c.Set("permissions", claims.Permissions)
		c.Next()
	}
}
func (m *AuthMiddleware) RequireRole(role string) gin.HandlerFunc {
	return func(c *gin.Context) {
		rolesAny, exists := c.Get("roles")
		if !exists {
			c.AbortWithStatus(http.StatusForbidden)
			return
		}

		roles, ok := rolesAny.([]string)
		if !ok {
			c.AbortWithStatus(http.StatusForbidden)
			return
		}
		for _, r := range roles {
			if r == role {
				c.Next()
				return
			}
		}

		c.AbortWithStatus(http.StatusForbidden)
	}
}
func (m *AuthMiddleware) RequirePermission(permission string) gin.HandlerFunc {
	return func(c *gin.Context) {
		permsAny, exists := c.Get("permissions")
		if !exists {
			c.AbortWithStatus(http.StatusForbidden)
			return
		}

		perms, ok := permsAny.([]string)
		if !ok {
			c.AbortWithStatus(http.StatusForbidden)
			return
		}
		for _, p := range perms {
			if p == permission {
				c.Next()
				return
			}
		}

		c.AbortWithStatus(http.StatusForbidden)
	}
}
