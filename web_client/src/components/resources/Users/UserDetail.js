// src/components/resources/Users/UserDetail.js
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { fetchUserDetails, blockUser, unblockUser } from './UserAPI';

const UserDetail = () => {
    const { id } = useParams();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await fetchUserDetails(id);
                setUser(response.data);
            } catch (error) {
                console.error('Ошибка при загрузке данных пользователя:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const handleBlock = async () => {
        try {
            await blockUser(id);
            setUser((prevUser) => ({ ...prevUser, isBlocked: true }));
        } catch (error) {
            console.error('Ошибка при блокировке пользователя:', error);
        }
    };

    const handleUnblock = async () => {
        try {
            await unblockUser(id);
            setUser((prevUser) => ({ ...prevUser, isBlocked: false }));
        } catch (error) {
            console.error('Ошибка при разблокировке пользователя:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Информация о пользователе</h1>
            <p>ФИО: {user.fullName}</p>
            <p>ID: {user.id}</p>
            <p>Статус: {user.isBlocked ? 'Заблокирован' : 'Активен'}</p>

            <div>
                <h2>Блокировка пользователя</h2>
                {user.isBlocked ? (
                    <button onClick={handleUnblock}>Разблокировать</button>
                ) : (
                    <button onClick={handleBlock}>Заблокировать</button>
                )}
            </div>

            <Link to={`/users/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

export default UserDetail;