import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ErrorPage from './errors/ErrorPage';
import { useNavigate } from 'react-router-dom';
import './styles/Dashboard.css';
import Disciplines from './resources/Disciplines/Disciplines';

const Dashboard = ({ userData }) => { 
    const [userDetails, setUserDetails] = useState({
        idx: null, 
        first_name: '',
        last_name: '',
        middle_name: '',
        roles: []
    });
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        middle_name: ''
    });
    const [token, setToken] = useState(null);

    const navigate = useNavigate();

    useEffect(() => {
        const checkSession = async () => {
            try {
                const sessionResponse = await axios.get('/api/session', { withCredentials: true });
                console.log('Проверка сессии:', sessionResponse.data); 
                if (sessionResponse.data.status === 'authorized') {
                    const userId = sessionResponse.data.userInfo.idx; 
                    console.log('Полученный userId:', userId); 
        
                    const receivedToken = sessionResponse.data.token;
                    setToken(receivedToken); 
                    await fetchUserData(userId, receivedToken); 
                } else {
                    navigate('/'); 
                }
            } catch (err) {
                console.error('Ошибка проверки сессии:', err);
                setError(true); 
            } finally {
                setLoading(false);
            }
        };

        checkSession();
    }, [navigate]);

    const fetchUserData = async (userId, token) => {
        try {
            const userResponse = await axios.get(`/api/db/users/${userId}/name`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log('Ответ от API пользователя:', userResponse.data); // Логируем полный ответ
    
            const user = userResponse.data;
    
            console.log('Полученные данные пользователя:', user);
    
            if (user) {
                console.log('Пользователь найден:', user);
                setUserDetails(prevDetails => ({
                    ...prevDetails,
                    idx: user.idx, 
                    first_name: user.first_name,
                    last_name: user.last_name,
                    middle_name: user.middle_name,
                    roles: Array.isArray(user.roles) ? user.roles : []
                }));
                setFormData({
                    first_name: user.first_name,
                    last_name: user.last_name,
                    middle_name: user.middle_name
                });
            } else {
                console.error('Пользователь не найден');
                setError(true);
            }
        } catch (error) {
            console.error('Ошибка при получении данных пользователя:', error.response ? error.response.data : error.message);
            setError(true);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleEdit = () => {
        setIsEditing(true);
    };

    useEffect(() => {
        console.log('userDetails после обновления:', userDetails); 
    }, [userDetails]);

    const handleSave = async () => {
        console.log('userDetails перед сохранением:', userDetails); 
        const userId = userDetails.idx; 
        console.log('userId перед сохранением:', userId);
        
        if (!userId) {
            console.error('ID пользователя не найден');
            throw new Error('ID пользователя не найден');
        }
    
        const fullName = {
            first_name: formData.first_name,
            last_name: formData.last_name,
            middle_name: formData.middle_name
        };
    
        try {
            const response = await axios.put(`/api/users/${userId}/name/update`, fullName, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
    
            console.log('Ответ при обновлении данных:', response.data);
            setUserDetails(prevDetails => ({ ...prevDetails, ...formData })); 
            setIsEditing(false);
        } catch (error) {
            console.error('Ошибка при сохранении данных:', error.response ? error.response.data : error.message);
        }
    };

    const handleCancel = () => {
        setIsEditing(false);
        setFormData({
            first_name: userDetails.first_name,
            last_name: userDetails.last_name,
            middle_name: userDetails.middle_name
        });
    };

    if (loading) return <div>Загрузка...</div>;
    if (error) return <ErrorPage />;

    return (
        <div className="dashboard-container">
            <h2>Личный кабинет</h2>
            <div className="user-info">
                <p>
                    <strong>Имя: </strong>
                    {isEditing ? (
                        <input
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            className="input-field"
                        />
                    ) : (
                        <span>{userDetails.first_name}</span>
                    )}
                </p>
                <p>
                    <strong>Фамилия: </strong>
                    {isEditing ? (
                        <input
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                            className="input-field"
                        />
                    ) : (
                        <span>{userDetails.last_name}</span>
                    )}
                </p>
                <p>
                    <strong>Отчество: </strong>
                    {isEditing ? (
                        <input
                            type="text"
                            name="middle_name"
                            value={formData.middle_name}
                            onChange={handleChange}
                            className="input-field"
                        />
                    ) : (
                        <span>{userDetails.middle_name}</span>
                    )}
                </p>
            </div>
            {isEditing ? (
                <div className="button-group">
                    <button className="logout-button" onClick={handleSave}>Сохранить</button>
                    <button className="logout-button" onClick={handleCancel}>Назад</button>
                </div>
            ) : (
                <button className="logout-button" onClick={handleEdit}>Изменить</button>
            )}

            <Disciplines 
                userRole={userDetails.roles.includes('Teacher') ? 'Teacher' : 'Student'} 
                userId={userDetails.idx} 
            />

            <button className="logout-button" onClick={() => navigate('/logout')}>Выйти</button>
        </div>
    );
};

export default Dashboard;