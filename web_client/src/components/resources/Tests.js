import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Tests = () => {
    const [tests, setTests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTests();
    }, []);

    const fetchTests = () => {
        setLoading(true);
        axios
            .get('/api/tests')
            .then((response) => {
                setTests(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка тестов:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <Routes>
            {/* Список тестов */}
            <Route
                path="/"
                element={
                    <div>
                        <h1>Список тестов</h1>
                        <ul>
                            {tests.map((test) => (
                                <li key={test.id}>
                                    <Link to={`/tests/${test.id}`}>{test.name}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />

            {/* Детали теста */}
            <Route path="/:id" element={<TestDetail />} />

            {/* Редактирование теста */}
            <Route path="/:id/edit" element={<TestEdit />} />
        </Routes>
    );
};

const TestDetail = () => {
    const { id } = useParams();
    const [test, setTest] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/tests/${id}`)
            .then((response) => {
                setTest(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных теста:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали теста</h1>
            <p>Название: {test.name}</p>
            <p>Описание: {test.description}</p>
            <Link to={`/tests/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

const TestEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/tests/${id}`)
            .then((response) => {
                setName(response.data.name);
                setDescription(response.data.description);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных теста:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    const handleSave = () => {
        axios
            .put(`/api/tests/${id}`, { name, description })
            .then(() => {
                navigate(`/tests/${id}`);
            })
            .catch((error) => {
                console.error('Ошибка при сохранении данных теста:', error);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование теста</h1>
            <div>
                <label>Название:</label>
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
            </div>
            <div>
                <label>Описание:</label>
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
            </div>
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default Tests;