import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAttemptById, updateAttempt } from './AttemptAPI';

const AttemptEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [attempt, setAttempt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await updateAttempt(id, attempt);
            navigate(`/attempts/${id}`); // Перенаправляем на детали попытки после успешного редактирования
        } catch (err) {
            setError('Ошибка при обновлении попытки.');
        }
    };

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Редактирование попытки</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>ID пользователя:</label>
                    <input
                        type="text"
                        value={attempt.userId}
                        onChange={(e) => setAttempt({ ...attempt, userId: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label>ID теста:</label>
                    <input
                        type="text"
                        value={attempt.testId}
                        onChange={(e) => setAttempt({ ...attempt, testId: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label>Статус:</label>
                    <input
                        type="text"
                        value={attempt.status}
                        onChange={(e) => setAttempt({ ...attempt, status: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label>Ответы (через запятую):</label>
                    <input
                        type="text"
                        value={attempt.answers.join(', ')}
                        onChange={(e) => setAttempt({ ...attempt, answers: e.target.value.split(',').map(answer => answer.trim()) })}
                        required
                    />
                </div>
                <button type="submit">Сохранить</button>
                {error && <p style={{ color: 'red' }}>{error}</p>}
            </form>
        </div>
    );
};

export default AttemptEdit;