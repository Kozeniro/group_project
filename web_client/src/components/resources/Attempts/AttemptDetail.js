import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAttemptById } from './AttemptAPI';

const AttemptDetail = () => {
    const { id } = useParams();
    const [attempt, setAttempt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const loadAttempt = async () => {
            try {
                const data = await fetchAttemptById(id);
                setAttempt(data);
            } catch (err) {
                setError('Ошибка при загрузке данных попытки.');
            } finally {
                setLoading(false);
            }
        };

        loadAttempt();
    }, [id]);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Детали попытки</h1>
            <p>ID: {attempt.id}</p>
            <p>Пользователь: {attempt.userId}</p>
            <p>Тест: {attempt.testId}</p>
            <p>Статус: {attempt.status}</p>
            <p>Ответы: {attempt.answers.join(', ')}</p>
            <button onClick={() => navigate(`/attempts/${id}/edit`)}>Редактировать</button>
            <button onClick={() => navigate('/attempts')}>Назад</button>
        </div>
    );
};

export default AttemptDetail;