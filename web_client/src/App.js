import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import axios from 'axios';

import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AuthCallback from './components/auth/AuthCallback';
import Unauthorized from './components/errors/Unauthorized';
import Forbidden from './components/errors/Forbidden';
import ErrorPage from './components/errors/ErrorPage';
import Logout from './components/Logout';
import Users from './components/resources/Users';
import Disciplines from './components/resources/Disciplines';
import Tests from './components/resources/Tests';
import Questions from './components/resources/Questions';
import Attempts from './components/resources/Attempts';
import Answers from './components/resources/Answers';

const App = () => {
    const [userStatus, setUserStatus] = useState('unknown');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const sessionToken = document.cookie
            .split('; ')
            .find((row) => row.startsWith('session_token='))
            ?.split('=')[1];

        if (!sessionToken) {
            setUserStatus('unknown');
            setLoading(false);
            return;
        }

        axios
            .get('/api/session', {
                headers: { Authorization: `Bearer ${sessionToken}` },
            })
            .then((response) => {
                setUserStatus(response.data.status); // 'anonymous' или 'authorized'
            })
            .catch(() => {
                setUserStatus('unknown');
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div>Загрузка...</div>;
    }

    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home userStatus={userStatus} />} />
                <Route path="/dashboard" element={userStatus === 'authorized' ? <Dashboard /> : <Navigate to="/unauthorized" />} />
                <Route path="/logout" element={<Logout all={false} setUserStatus={setUserStatus} />} />
                <Route path="/auth/github/callback" element={<AuthCallback setUserStatus={setUserStatus} />} />

                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route path="/forbidden" element={<Forbidden />} />
                <Route path="/error" element={<ErrorPage />} />

                {/* Все ресурсы теперь находятся в одной папке */}
                <Route path="/users/*" element={<Users />} />
                <Route path="/disciplines/*" element={<Disciplines />} />
                <Route path="/tests/*" element={<Tests />} />
                <Route path="/questions/*" element={<Questions />} />
                <Route path="/attempts/*" element={<Attempts />} />
                <Route path="/answers/*" element={<Answers />} />

                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
};