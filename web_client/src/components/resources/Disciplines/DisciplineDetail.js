import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    fetchDisciplineDetails,
    fetchDisciplineTests,
    fetchDisciplineUsers,
    activateTest,
    deactivateTest,
    deleteTest,
    enrollUser,
    unenrollUser,
    checkTestActiveStatus
} from './DisciplineAPI';

const DisciplineDetail = () => {
    const { id } = useParams();
    const [discipline, setDiscipline] = useState(null);
    const [tests, setTests] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const disciplineResponse = await fetchDisciplineDetails(id);
                setDiscipline(disciplineResponse.data);
                const testsResponse = await fetchDisciplineTests(id);
                const usersResponse = await fetchDisciplineUsers(id);
                setTests(testsResponse.data);
                setUsers(usersResponse.data);
            } catch (error) {
                console.error('Ошибка при загрузке данных дисциплины:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    const handleActivateTest = async (testId) => {
        try {
            await activateTest(id, testId);
            const isActive = await checkTestActiveStatus(id, testId);
            setTests((prevTests) =>
                prevTests.map((test) =>
                    test.id === testId ? { ...test, isActive: isActive.data.isActive } : test
                )
            );
        } catch (error) {
            console.error('Ошибка при активации теста:', error);
        }
    };

    const handleDeactivateTest = async (testId) => {
        try {
            await deactivateTest(id, testId);
            const isActive = await checkTestActiveStatus(id, testId);
            setTests((prevTests) =>
                prevTests.map((test) =>
                    test.id === testId ? { ...test, isActive: isActive.data.isActive } : test
                )
            );
        } catch (error) {
            console.error('Ошибка при деактивации теста:', error);
        }
    };

    const handleDeleteTest = async (testId) => {
        try {
            await deleteTest(id, testId);
            setTests((prevTests) => prevTests.filter((test) => test.id !== testId));
        } catch (error) {
            console.error('Ошибка при удалении теста:', error);
        }
    };

    const handleEnrollUser = async (userId) => {
        try {
            await enrollUser(id, userId);
            setUsers((prevUsers) =>
                prevUsers.map((user) =>
                    user.id === userId ? { ...user, isEnrolled: true } : user
                )
            );
        } catch (error) {
            console.error('Ошибка при записи пользователя:', error);
        }
    };

    const handleUnenrollUser = async (userId) => {
        try {
            await unenrollUser(id, userId);
            setUsers((prevUsers) =>
                prevUsers.map((user) =>
                    user.id === userId ? { ...user, isEnrolled: false } : user
                )
            );
        } catch (error) {
            console.error('Ошибка при отчислении пользователя:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали дисциплины</h1>
            <p>Название: {discipline.name}</p>
            <p>Описание: {discipline.description}</p>
            <Link to={`/disciplines/${id}/edit`}>Редактировать</Link>

            <h2>Тесты дисциплины</h2>
            <ul>
                {tests.map((test) => (
                    <li key={test.id}>
                        <p>Название теста: {test.name}</p>
                        <p>Статус: {test.isActive ? 'Активен' : 'Неактивен'}</p>
                        <button onClick={() => handleActivateTest(test.id)}>Активировать</button>
                        <button onClick={() => handleDeactivateTest(test.id)}>Деактивировать</button>
                        <button onClick={() => handleDeleteTest(test.id)}>Удалить</button>
                    </li>
                ))}
            </ul>

            <h2>Пользователи дисциплины</h2>
            <ul>
                {users.map((user) => (
                    <li key={user.id}>
                        <p>ФИО: {user.fullName}</p>
                        <p>Статус: {user.isEnrolled ? 'Записан' : 'Не записан'}</p>
                        <button onClick={() => handleEnrollUser(user.id)}>Записать</button>
                        <button onClick={() => handleUnenrollUser(user.id)}>Отчислить</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DisciplineDetail;