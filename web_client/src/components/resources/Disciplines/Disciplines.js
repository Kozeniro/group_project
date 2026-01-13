import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchUserDisciplines } from './DisciplineAPI'; // Импортируйте новый API метод

const Disciplines = ({ userRole, userId }) => {
    const [disciplines, setDisciplines] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDisciplinesData();
    }, []);

    const fetchDisciplinesData = async () => {
        setLoading(true);
        try {
            const response = await fetchUserDisciplines(userId); // Используем переданный userId
            console.log('Response from fetchUserDisciplines:', response); // Логируем ответ
            
            if (response && Array.isArray(response.disciplines)) {
                setDisciplines(response.disciplines); // Устанавливаем дисциплины из ответа
            } else {
                console.warn('Полученный ответ не содержит дисциплин:', response);
                setDisciplines([]); // Устанавливаем пустой массив, если дисциплины отсутствуют
            }
        } catch (error) {
            console.error('Ошибка при загрузке списка дисциплин:', error.response ? error.response.data : error.message);
            setDisciplines([]); // Устанавливаем пустой массив в случае ошибки
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Загрузка...</div>;
    if (disciplines.length === 0) return <div>Нет доступных дисциплин.</div>;

    return (
        <div>
            <h3>Доступные дисциплины</h3>
            <ul>
                {disciplines.map((discipline) => (
                    <li key={discipline.id}>
                        <Link to={`/disciplines/${discipline.id}`}>{discipline.name}</Link>
                    </li>
                ))}
            </ul>
            {userRole.includes('Teacher') && ( // Проверяем, есть ли роль 'Teacher'
                <Link to="/disciplines/create">Создать дисциплину</Link>
            )}
        </div>
    );
};

export default Disciplines;