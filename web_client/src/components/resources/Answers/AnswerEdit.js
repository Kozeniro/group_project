import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAnswerById, updateAnswer } from './AnswerAPI';

const AnswerEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [answer, setAnswer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await updateAnswer(id, answer);
            navigate(`/answers/${id}`); // Перенаправляем на детали ответа после успешного редактирования
        } catch (err) {
            setError('Ошибка при обновлении ответа.');
        }
    };

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Редактирование ответа</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>ID вопроса:</label>
                    <input
                        type="text"
                        value={answer.questionId}
                        onChange={(e) => setAnswer({ ...answer, questionId: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label>ID попытки:</label>
                    <input
                        type="text"
                        value={answer.attemptId}
                        onChange={(e) => setAnswer({ ...answer, attemptId: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label>Ответ:</label>
                    <textarea
                        value={answer.value}
                        onChange={(e) => setAnswer({ ...answer, value: e.target.value })}
                        required
                    />
                </div>
                <button type="submit">Сохранить</button>
                {error && <p style={{ color: 'red' }}>{error}</p>}
            </form>
        </div>
    );
};

export default AnswerEdit;