import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAttempt } from './AttemptAPI';

const AttemptCreate = () => {
    const navigate = useNavigate();
    const [userId, setUserId] = useState('');
    const [testId, setTestId] = useState('');
    const [status, setStatus] = useState('');
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await createAttempt({ userId, testId, status, answers });
            navigate('/attempts'); // Перенаправляем на список попыток после успешного создания
        } catch (err) {
            setError('Ошибка при создании попытки.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Создание попытки</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>ID пользователя:</label>
                    <input
                        type="text"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>ID теста:</label>
                    <input
                        type="text"
                        value={testId}
                        onChange={(e) => setTestId(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Статус:</label>
                    <input
                        type="text"
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Ответы (через запятую):</label>
                    <input
                        type="text"
                        value={answers.join(', ')}
                        onChange={(e) => setAnswers(e.target.value.split(',').map(answer => answer.trim()))}
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

export default AttemptCreate;