import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAnswer } from './AnswerAPI';

const AnswerCreate = () => {
    const navigate = useNavigate();
    const [questionId, setQuestionId] = useState('');
    const [attemptId, setAttemptId] = useState('');
    const [value, setValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await createAnswer({ questionId, attemptId, value });
            navigate('/answers'); // Перенаправляем на список ответов после успешного создания
        } catch (err) {
            setError('Ошибка при создании ответа.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Создание ответа</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>ID вопроса:</label>
                    <input
                        type="text"
                        value={questionId}
                        onChange={(e) => setQuestionId(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>ID попытки:</label>
                    <input
                        type="text"
                        value={attemptId}
                        onChange={(e) => setAttemptId(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Ответ:</label>
                    <textarea
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? 'Создание...' : 'Создать'}
                </button>
                {error && <p style={{ color: 'red' }}>{error}</p>}
            </form>
        </div>
    );
};

export default AnswerCreate;