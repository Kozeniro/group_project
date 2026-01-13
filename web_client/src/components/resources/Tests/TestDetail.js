// src/components/resources/Tests/TestDetail.js
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchTestDetails } from './TestAPI';

const TestDetail = () => {
    const { id } = useParams();
    const [test, setTest] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadTestDetails = async () => {
            setLoading(true);
            try {
                const response = await fetchTestDetails(id);
                setTest(response.data);
            } catch (error) {
                console.error('Ошибка при загрузке данных теста:', error);
            } finally {
                setLoading(false);
            }
        };

        loadTestDetails();
    }, [id]);

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Детали теста</h1>
            <p>Название: {test.name}</p>
            <p>Описание: {test.description}</p>
            <Link to={`/tests/${id}/edit`}>Редактировать</Link>
        </div>
    );
};

export default TestDetail;