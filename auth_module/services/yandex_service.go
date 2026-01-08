package services

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"strings"
)

type YandexService struct {
	clientID     string
	clientSecret string
	redirectURL  string
}

func NewYandexService(
	clientID string,
	clientSecret string,
	redirectURL string,
) *YandexService {
	return &YandexService{
		clientID:     clientID,
		clientSecret: clientSecret,
		redirectURL:  redirectURL,
	}
}

/* ===== Exchange code → access token ===== */

func (s *YandexService) ExchangeCode(
	ctx context.Context,
	code string,
) (string, error) {

	data := url.Values{}
	data.Set("grant_type", "authorization_code")
	data.Set("client_id", s.clientID)
	data.Set("client_secret", s.clientSecret)
	data.Set("code", code)
	data.Set("redirect_uri", s.redirectURL)

	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		"https://oauth.yandex.ru/token",
		strings.NewReader(data.Encode()),
	)
	if err != nil {
		return "", err
	}

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
		return "", errors.New("no access token from yandex")
	}

	return result.AccessToken, nil
}

/* ===== Get Yandex user ===== */

func (s *YandexService) GetUser(
	ctx context.Context,
	accessToken string,
) (*YandexUser, error) {

	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodGet,
		"https://login.yandex.ru/info?format=json",
		nil,
	)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "OAuth "+accessToken)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var user YandexUser
	if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
		return nil, err
	}

	return &user, nil
}
