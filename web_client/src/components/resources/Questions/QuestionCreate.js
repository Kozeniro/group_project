import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createQuestion } from './QuestionAPI'; 

const QuestionCreate = ({ fetchQuestions }) => {
    const navigate = useNavigate();
    const [text, setText] = useState('');
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSave = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await createQuestion({ text, answers });
            fetchQuestions(); // Обновляем список вопросов
            navigate(`/questions/${response.id}/${response.version}`); // Переход на созданный вопрос
        } catch (err) {
            setError('Ошибка при создании вопроса.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Создание нового вопроса</h1>
            <div>
                <label>Текст вопроса:</label>
                <input
                    type="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />
            </div>
            <div>
                <label>Варианты ответов:</label>
                <textarea
                    value={answers.join('\n')}
                    onChange={(e) => setAnswers(e.target.value.split('\n'))}
                />
            </div>
            <button onClick={handleSave} disabled={loading}>
                {loading ? 'Создание...' : 'Создать'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default QuestionCreate;