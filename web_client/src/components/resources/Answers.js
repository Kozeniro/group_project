import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams } from 'react-router-dom';
import axios from 'axios';

const Answers = () => {
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnswers();
    }, []);

    const fetchAnswers = () => {
        setLoading(true);
        axios
            .get('/api/answers')
            .then((response) => {
                setAnswers(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка ответов:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <Routes>
            {/* Список ответов */}
            <Route
                path="/"
                element={
                    <div>
                        <h1>Список ответов</h1>
                        <ul>
                            {answers.map((answer) => (
                                <li key={answer.id}>
                                    <Link to={`/answers/${answer.id}`}>Ответ ID: {answer.id}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />

            {/* Детали ответа */}
            <Route path="/:id" element={<AnswerDetail />} />
        </Routes>
    );
};

const AnswerDetail = () => {
    const { id } = useParams();
    const [answer, setAnswer] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/answers/${id}`)
            .then((response) => {
                setAnswer(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных ответа:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали ответа</h1>
            <p>ID: {answer.id}</p>
            <p>Вопрос: {answer.questionId}</p>
            <p>Попытка: {answer.attemptId}</p>
            <p>Ответ: {answer.value}</p>
        </div>
    );
};

export default Answers;