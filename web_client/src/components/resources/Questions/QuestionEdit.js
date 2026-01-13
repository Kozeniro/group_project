import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchQuestionByIdAndVersion, updateQuestion } from './QuestionAPI'; 

const QuestionEdit = () => {
    const { id, version } = useParams();
    const navigate = useNavigate();
    const [text, setText] = useState('');
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadQuestion = async () => {
            setLoading(true);
            try {
                const data = await fetchQuestionByIdAndVersion(id, version);
                setText(data.text);
                setAnswers(data.answers);
            } catch (error) {
                console.error('Ошибка при загрузке данных вопроса:', error);
            } finally {
                setLoading(false);
            }
        };

        loadQuestion();
    }, [id, version]);

    const handleSave = async () => {
        try {
            const response = await updateQuestion(id, { text, answers });
            navigate(`/questions/${id}/${response.version}`);
        } catch (error) {
            console.error('Ошибка при сохранении данных вопроса:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование вопроса</h1>
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
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default QuestionEdit;