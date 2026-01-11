import React from 'react';
import { useSelector } from 'react-redux'; // Предполагаем, что вы используете Redux для управления состоянием

const SomeComponent = () => {
    const userRoles = useSelector(state => state.user.roles); // Получаем роли пользователя из состояния

    const canViewUsers = userRoles.some(role => permissions[role]['user:list:read']);

    if (!canViewUsers) {
        return <div>У вас нет доступа к этому ресурсу.</div>;
    }

    return (
        <div>
            <h2>Список пользователей</h2>
            {/* Логика для отображения списка пользователей */}
        </div>
    );
};

export default SomeComponent;