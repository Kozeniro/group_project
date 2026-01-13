import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAnswerById } from './AnswerAPI';

const AnswerDetail = () => {
    const { id } = useParams();
    const [answer, setAnswer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const loadAnswer = async () => {
            try {
                const data = await fetchAnswerById(id);
                setAnswer(data);
            } catch (err) {
                setError('Ошибка при загрузке данных ответа.');
            } finally {
                setLoading(false);
            }
        };

        loadAnswer();
    }, [id]);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Детали ответа</h1>
            <p>ID: {answer.id}</p>
            <p>Вопрос: {answer.questionId}</p>
            <p>Попытка: {answer.attemptId}</p>
            <p>Ответ: {answer.value}</p>
            <button onClick={() => navigate('/answers')}>Назад</button>
        </div>
    );
};

export default AnswerDetail;