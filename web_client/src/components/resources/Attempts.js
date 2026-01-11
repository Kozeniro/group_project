import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Attempts = () => {
    const [attempts, setAttempts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAttempts();
    }, []);

    const fetchAttempts = () => {
        setLoading(true);
        axios
            .get('/api/attempts')
            .then((response) => {
                setAttempts(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка попыток:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <Routes>
            {/* Список попыток */}
            <Route
                path="/"
                element={
                    <div>
                        <h1>Список попыток</h1>
                        <ul>
                            {attempts.map((attempt) => (
                                <li key={attempt.id}>
                                    <Link to={`/attempts/${attempt.id}`}>Попытка ID: {attempt.id}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />

            {/* Детали попытки */}
            <Route path="/:id" element={<AttemptDetail />} />
        </Routes>
    );
};

const AttemptDetail = () => {
    const { id } = useParams();
    const [attempt, setAttempt] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/attempts/${id}`)
            .then((response) => {
                setAttempt(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных попытки:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали попытки</h1>
            <p>ID: {attempt.id}</p>
            <p>Пользователь: {attempt.userId}</p>
            <p>Тест: {attempt.testId}</p>
            <p>Статус: {attempt.status}</p>
            <p>Ответы: {attempt.answers.join(', ')}</p>
        </div>
    );
};

export default Attempts;