// src/components/resources/Users/Users.js
import React, { useEffect, useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import UserDetail from './UserDetail';
import UserEdit from './UserEdit';
import { fetchUsers } from './UserAPI';

const Users = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUsersData();
    }, []);

    const fetchUsersData = async () => {
        setLoading(true);
        try {
            const response = await fetchUsers();
            console.log("                 ======================>                 ");
            setUsers(response.data);
        } catch (error) {
            console.error('Ошибка при загрузке списка пользователей:', error);
        } finally {
            setLoading(false);
        }
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

export default Users;