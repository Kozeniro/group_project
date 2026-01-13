import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { fetchUserRoles, saveUser, fetchAvailableRoles } from './UserAPI';

const UserEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [fullName, setFullName] = useState('');
    const [roles, setRoles] = useState([]);
    const [availableRoles, setAvailableRoles] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const userResponse = await axios.get(`/api/users/${id}/name`);
                const rolesResponse = await fetchUserRoles(id);
                const availableRolesResponse = await fetchAvailableRoles();

                setFullName(userResponse.data.fullName);
                setRoles(rolesResponse.data);
                setAvailableRoles(availableRolesResponse.data);
            } catch (error) {
                console.error('Ошибка при загрузке данных пользователя:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const handleSave = async () => {
        try {
            await saveUser(id, { fullName, roles });
            navigate(`/users/${id}`);
        } catch (error) {
            console.error('Ошибка при сохранении данных пользователя:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование пользователя</h1>
            <div>
                <label>ФИО:</label>
                <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                />
            </div>
            <div>
                <label>Роли:</label>
                <select
                    multiple
                    value={roles}
                    onChange={(e) => setRoles(Array.from(e.target.selectedOptions, (option) => option.value))}
                >
                    {availableRoles.map((role) => (
                        <option key={role.id} value={role.id}>
                            {role.name}
                        </option>
                    ))}
                </select>
            </div>
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default UserEdit;