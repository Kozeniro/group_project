import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Questions = () => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchQuestions();
    }, []);

    const fetchQuestions = () => {
        setLoading(true);
        axios
            .get('/api/questions')
            .then((response) => {
                setQuestions(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка вопросов:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <Routes>
            <Route
                path="/"
                element={
                    <div>
                        <h1>Список вопросов</h1>
                        <ul>
                            {questions.map((question) => (
                                <li key={question.id}>
                                    <Link to={`/questions/${question.id}`}>{question.text}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />
            <Route path="/:id" element={<QuestionDetail />} />
            <Route path="/:id/edit" element={<QuestionEdit />} />
        </Routes>
    );
};

const QuestionDetail = () => {
    const { id } = useParams();
    const [question, setQuestion] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/questions/${id}`)
            .then((response) => {
                setQuestion(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных вопроса:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали вопроса</h1>
            <p>Текст вопроса: {question.text}</p>
            <p>ID: {question.id}</p>
            <Link to={`/questions/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

const QuestionEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/questions/${id}`)
            .then((response) => {
                setText(response.data.text);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных вопроса:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    const handleSave = () => {
        axios
            .put(`/api/questions/${id}`, { text })
            .then(() => {
                navigate(`/questions/${id}`);
            })
            .catch((error) => {
                console.error('Ошибка при сохранении данных вопроса:', error);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование вопроса</h1>
            <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
            />
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default Questions;