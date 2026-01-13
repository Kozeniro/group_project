import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchQuestionByIdAndVersion } from './QuestionAPI'; 

const QuestionDetail = () => {
    const { id, version } = useParams();
    const [question, setQuestion] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadQuestion = async () => {
            setLoading(true);
            try {
                const data = await fetchQuestionByIdAndVersion(id, version);
                setQuestion(data);
            } catch (error) {
                console.error('Ошибка при загрузке данных вопроса:', error);
            } finally {
                setLoading(false);
            }
        };

        loadQuestion();
    }, [id, version]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали вопроса</h1>
            <p>Текст вопроса: {question.text}</p>
            <p>ID: {question.id}</p>
            <p>Версия: {question.version}</p>
            <Link to={`/questions/${id}/${version}/edit`}>Редактировать</Link>
        </div>
    );
};

export default QuestionDetail;