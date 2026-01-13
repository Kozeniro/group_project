import React, { useEffect, useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { fetchTests } from './TestAPI';
import TestDetail from './TestDetail';
import TestEdit from './TestEdit';

const Tests = () => {
    const [tests, setTests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadTests = async () => {
            setLoading(true);
            try {
                const response = await fetchTests();
                setTests(response.data);
            } catch (error) {
                console.error('Ошибка при загрузке списка тестов:', error);
            } finally {
                setLoading(false);
            }
        };

        loadTests();
    }, []);

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

export default Tests;