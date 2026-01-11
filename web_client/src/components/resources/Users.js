import React, { useEffect, useState } from 'react';
import { Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Users = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = () => {
        setLoading(true);
        axios
            .get('/api/users')
            .then((response) => {
                setUsers(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке списка пользователей:', error);
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
                        <h1>Список пользователей</h1>
                        <ul>
                            {users.map((user) => (
                                <li key={user.id}>
                                    <Link to={`/users/${user.id}`}>{user.fullName}</Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                }
            />
            <Route path="/:id" element={<UserDetail />} />
            <Route path="/:id/edit" element={<UserEdit />} />
        </Routes>
    );
};

const UserDetail = () => {
    const { id } = useParams();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/users/${id}`)
            .then((response) => {
                setUser(response.data);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных пользователя:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Информация о пользователе</h1>
            <p>ФИО: {user.fullName}</p>
            <p>ID: {user.id}</p>
            <Link to={`/users/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

const UserEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [fullName, setFullName] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        axios
            .get(`/api/users/${id}`)
            .then((response) => {
                setFullName(response.data.fullName);
            })
            .catch((error) => {
                console.error('Ошибка при загрузке данных пользователя:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [id]);

    const handleSave = () => {
        axios
            .put(`/api/users/${id}`, { fullName })
            .then(() => {
                navigate(`/users/${id}`);
            })
            .catch((error) => {
                console.error('Ошибка при сохранении данных пользователя:', error);
            });
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование пользователя</h1>
            <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
            />
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default Users;