import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Disciplines = () => {
    const [disciplines, setDisciplines] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDisciplines();
    }, []);

    const fetchDisciplines = () => {
        setLoading(true);
        axios
            .get('/api/disciplines')
            .then((response) => {
                setDisciplines(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка дисциплин:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <Routes>
            {/* Список дисциплин */}
            <Route
                path="/"
                element={
                    <div>
                        <h1>Список дисциплин</h1>
                        <ul>
                            {disciplines.map((discipline) => (
                                <li key={discipline.id}>
                                    <Link to={`/disciplines/${discipline.id}`}>{discipline.name}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />

            {/* Детали дисциплины */}
            <Route path="/:id" element={<DisciplineDetail />} />

            {/* Редактирование дисциплины */}
            <Route path="/:id/edit" element={<DisciplineEdit />} />
        </Routes>
    );
};

const DisciplineDetail = () => {
    const { id } = useParams();
    const [discipline, setDiscipline] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/disciplines/${id}`)
            .then((response) => {
                setDiscipline(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных дисциплины:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали дисциплины</h1>
            <p>Название: {discipline.name}</p>
            <p>Описание: {discipline.description}</p>
            <Link to={`/disciplines/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

const DisciplineEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/disciplines/${id}`)
            .then((response) => {
                setName(response.data.name);
                setDescription(response.data.description);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных дисциплины:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    const handleSave = () => {
        axios
            .put(`/api/disciplines/${id}`, { name, description })
            .then(() => {
                navigate(`/disciplines/${id}`);
            })
            .catch((error) => {
                console.error('Ошибка при сохранении данных дисциплины:', error);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование дисциплины</h1>
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

export default Disciplines;