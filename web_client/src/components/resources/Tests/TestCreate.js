import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTest } from './TestAPI';
import axios from 'axios';

const TestCreate = ({ permissions }) => {
    const navigate = useNavigate();
    const [testName, setTestName] = useState('');
    const [testId, setTestId] = useState(null);
    const [questions, setQuestions] = useState([{ question: '', answers: [''], correctAnswer: 0 }]);

    // Проверка наличия permissions
    if (!permissions || !Array.isArray(permissions)) {
        return <div>Ошибка: отсутствуют права доступа.</div>;
    }

    // Создание теста
    const handleCreateTest = async () => {
        if (!permissions.includes('test:add')) {
            alert('У вас нет доступа для создания теста.');
            return;
        }
        try {
            const response = await createTest({ name: testName });
            setTestId(response.data.id); // Сохраняем ID созданного теста
            alert('Тест успешно создан! Теперь добавьте вопросы.');
        } catch (error) {
            console.error('Ошибка при создании теста:', error);
            alert('Не удалось создать тест.');
        }
    };

    // Добавление вопроса
    const handleAddQuestion = () => {
        setQuestions(prev => [...prev, { question: '', answers: [''], correctAnswer: 0 }]);
    };

    // Добавление ответа
    const handleAddAnswer = (index) => {
        const newQuestions = [...questions];
        newQuestions[index].answers.push(''); 
        setQuestions(newQuestions);
    };

    // Сохранение вопросов
    const handleSaveQuestions = async () => {
        if (!testId) {
            alert('Сначала создайте тест.');
            return;
        }
        try {
            await axios.put(`/api/tests/${testId}/questions`, { questions });
            navigate('/tests'); // Перенаправляем на страницу тестов после добавления вопросов
        } catch (error) {
            console.error('Ошибка при добавлении вопросов:', error);
            alert('Не удалось добавить вопросы.');
        }
    };

    return (
        <div>
            <h2>Создать тест</h2>
            {!testId ? (
                <>
                    <input
                        type="text"
                        value={testName}
                        onChange={(e) => setTestName(e.target.value)}
                        placeholder="Название теста"
                    />
                    <button onClick={handleCreateTest}>Создать тест</button>
                </>
            ) : (
                <>
                    <h3>Добавьте вопросы для теста: {testName}</h3>
                    {questions.map((q, index) => (
                        <div key={index}>
                            <input
                                type="text"
                                value={q.question}
                                onChange={(e) => {
                                    const newQuestions = [...questions];
                                    newQuestions[index].question = e.target.value;
                                    setQuestions(newQuestions);
                                }}
                                placeholder="Вопрос"
                            />
                            {q.answers.map((answer, ansIndex) => (
                                <input
                                    key={ansIndex}
                                    type="text"
                                    value={answer}
                                    onChange={(e) => {
                                        const newQuestions = [...questions];
                                        newQuestions[index].answers[ansIndex] = e.target.value;
                                        setQuestions(newQuestions);
                                    }}
                                    placeholder={`Ответ ${ansIndex + 1}`}
                                />
                            ))}
                            <button onClick={() => handleAddAnswer(index)}>Добавить ответ</button>
                        </div>
                    ))}
                    <button onClick={handleAddQuestion}>Добавить вопрос</button>
                    <button onClick={handleSaveQuestions}>Сохранить вопросы</button>
                    <button onClick={() => navigate('/tests')}>Назад</button>
                </>
            )}
        </div>
    );
};

export default TestCreate;