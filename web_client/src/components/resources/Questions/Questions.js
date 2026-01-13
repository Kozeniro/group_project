import React, { useEffect, useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { fetchQuestions } from './QuestionAPI'; 
import QuestionDetail from './QuestionDetail';
import QuestionEdit from './QuestionEdit';
import QuestionCreate from './QuestionCreate';

const Questions = () => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadQuestions = async () => {
            setLoading(true);
            try {
                const data = await fetchQuestions();
                setQuestions(data);
            } catch (error) {
                console.error('Ошибка при загрузке списка вопросов:', error);
            } finally {
                setLoading(false);
            }
        };

        loadQuestions();
    }, []);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Список вопросов</h1>
            <ul>
                {questions.map((question) => (
                    <li key={question.id}>
                        <Link to={`/questions/${question.id}/${question.version}`}>
                            {question.text} (Версия: {question.version})
                        </Link>
                    </li>
                ))}
            </ul>
            <Link to="/questions/create">Создать новый вопрос</Link>
            <Routes>
                <Route path="/:id/:version" element={<QuestionDetail />} />
                <Route path="/:id/:version/edit" element={<QuestionEdit />} />
                <Route path="/create" element={<QuestionCreate fetchQuestions={fetchQuestions} />} />
            </Routes>
        </div>
    );
};

export default Questions;