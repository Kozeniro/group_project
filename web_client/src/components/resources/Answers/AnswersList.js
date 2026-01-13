import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchAnswers } from './AnswerAPI';

const AnswersList = () => {
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadAnswers = async () => {
            try {
                const data = await fetchAnswers();
                setAnswers(data);
            } catch (err) {
                setError('Ошибка при загрузке списка ответов.');
            } finally {
                setLoading(false);
            }
        };

        loadAnswers();
    }, []);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
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
    );
};

export default AnswersList;