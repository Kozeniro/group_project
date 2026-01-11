const express = require('express');
const session = require('express-session');
const passport = require('passport');
const GitHubStrategy = require('passport-github').Strategy;
const YandexStrategy = require('passport-yandex').Strategy;
const checkPermissions = require('./middleware/checkPermissions');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Настройка CORS
app.use(cors());

// Настройка сессий
app.use(session({ secret: 'secret_key', resave: false, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());

// Настройка стратегий
passport.use(new GitHubStrategy({
    clientID: 'Ov23libRIJj8xTzQLJsw',
    clientSecret: 'dd14119d306e30394bf64d16ee768d38648fe950',
    callbackURL: "http://localhost:3000/auth/github/callback"
}, (accessToken, refreshToken, profile, done) => {
    return done(null, profile);
}));

passport.use(new YandexStrategy({
    clientID: '60712c9fe7104b4aa8ee392ad5a96c02',
    clientSecret: '6a0537b5051c468a9d4ff60fb0e6bd96',
    callbackURL: "http://localhost:3000/auth/yandex/callback"
}, (accessToken, refreshToken, profile, done) => {
    return done(null, profile);
}));

// Сериализация пользователя
passport.serializeUser((user, done) => {
    done(null, user);
});

passport.deserializeUser((obj, done) => {
    done(null, obj);
});

// Генерация JWT токена
function generateToken(user) {
    return jwt.sign(user, 'your_jwt_secret', { expiresIn: '1h' });
}

// Middleware для проверки JWT
function authenticateJWT(req, res, next) {
    const token = req.headers.authorization && req.headers.authorization.split(' ')[1];
    if (token) {
        jwt.verify(token, 'your_jwt_secret', (err, user) => {
            if (err) {
                return res.sendStatus(403);
            }
            req.user = user;
            next();
        });
    } else {
        res.sendStatus(401);
    }
}

// Маршруты аутентификации
app.get('/auth/github', passport.authenticate('github'));

app.get('/auth/github/callback',
    passport.authenticate('github', { failureRedirect: '/' }),
    (req, res) => {
        const token = generateToken(req.user);
        res.redirect(`/dashboard?token=${token}`);
    });

app.get('/auth/yandex', passport.authenticate('yandex'));

app.get('/auth/yandex/callback',
    passport.authenticate('yandex', { failureRedirect: '/' }),
    (req, res) => {
        const token = generateToken(req.user);
        res.redirect(`/dashboard?token=${token}`);
    });

app.get('/', (req, res) => {
    res.send('<h1>Welcome</h1><a href="/auth/github">Login with GitHub</a><br><a href="/auth/yandex">Login with Yandex</a>');
});

// Маршрут для проверки сессии
app.get('/api/check-session', (req, res) => {
    if (req.isAuthenticated()) {
        res.json({ status: 'Авторизованный' });
    } else {
        res.json({ status: 'Не авторизованный' });
    }
});

// Пример защищенного маршрута
app.get('/api/users', authenticateJWT, checkPermissions('user:list:read'), (req, res) => {
    res.json({ message: 'Список пользователей' });
});

// Пример маршрута для просмотра данных о пользователе
app.get('/api/users/:id', authenticateJWT, checkPermissions('user:data:read'), (req, res) => {
    const userId = req.params.id;
    res.json({ message: `Данные о пользователе с ID ${userId}` });
});

// Маршрут для Dashboard
app.get('/dashboard', (req, res) => {
    const token = req.query.token;
    if (token) {
        res.send(`<h1>Dashboard</h1><p>Ваш токен: ${token}</p>`);
    } else {
        res.send('<h1>Dashboard</h1><p>Токен не найден.</p>');
    }
});

// Логирование запросов
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
});

// Запуск сервера
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});