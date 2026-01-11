import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import GitHubAuth from './components/GitHubAuth';
import YandexAuth from './components/YandexAuth';
import Unauthorized from './components/Unauthorized';
import Forbidden from './components/Forbidden';
import ErrorPage from './components/ErrorPage';

const App = () => {
    const [userStatus, setUserStatus] = useState('unknown');

    useEffect(() => {
        const sessionTokenRow = document.cookie.split('; ').find(row => row.startsWith('session_token='));
        const sessionToken = sessionTokenRow ? sessionTokenRow.split('=')[1] : null;

        if (sessionToken) {
            axios.get('http://localhost:3000/api/check-session', { headers: { Authorization: `Bearer ${sessionToken}` } })
                .then(response => {
                    if (response.data.status === 'Авторизованный') {
                        setUserStatus('authorized');
                    } else {
                        setUserStatus('unknown');
                    }
                })
                .catch((error) => {
                    console.error('Ошибка при проверке сессии:', error);
                    setUserStatus('unknown');
                });
        } else {
            setUserStatus('unknown');
        }
    }, []);

    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Navigate to="/" />} />
                <Route path="/dashboard" element={userStatus === 'authorized' ? <Dashboard /> : <Navigate to="/" />} />
                <Route path="/auth/github" element={<GitHubAuth />} />
                <Route path="/auth/yandex" element={<YandexAuth />} />
                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route path="/forbidden" element={<Forbidden />} />
                <Route path="/error" element={<ErrorPage />} />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
};

export default App;