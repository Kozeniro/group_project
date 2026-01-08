package services

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"strings"
)

type GitHubService struct {
	clientID     string
	clientSecret string
	redirectURL  string
}

func NewGitHubService(
	clientID string,
	clientSecret string,
	redirectURL string,
) *GitHubService {
	return &GitHubService{
		clientID:     clientID,
		clientSecret: clientSecret,
		redirectURL:  redirectURL,
	}
}

/* ===== Exchange code → access token ===== */

func (s *GitHubService) ExchangeCode(
	ctx context.Context,
	code string,
) (string, error) {

	data := url.Values{}
	data.Set("client_id", s.clientID)
	data.Set("client_secret", s.clientSecret)
	data.Set("code", code)
	data.Set("redirect_uri", s.redirectURL)

	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		"https://github.com/login/oauth/access_token",
		strings.NewReader(data.Encode()),
	)
	if err != nil {
		return "", err
	}

	req.Header.Set("Accept", "application/json")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result struct {
		AccessToken string `json:"access_token"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	if result.AccessToken == "" {
		return "", errors.New("no access token from github")
	}

	return result.AccessToken, nil
}

/* ===== Get GitHub user ===== */

func (s *GitHubService) GetUser(
	ctx context.Context,
	accessToken string,
) (*GitHubUser, error) {

	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodGet,
		"https://api.github.com/user",
		nil,
	)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Accept", "application/vnd.github+json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var user GitHubUser
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		return nil, err
	}

	return &user, nil
}
