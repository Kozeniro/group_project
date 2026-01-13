import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchAttempts } from './AttemptAPI';

const AttemptsList = () => {
    const [attempts, setAttempts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadAttempts = async () => {
            try {
                const data = await fetchAttempts();
                setAttempts(data);
            } catch (err) {
                setError('Ошибка при загрузке списка попыток.');
            } finally {
                setLoading(false);
            }
        };

        loadAttempts();
    }, []);

    if (loading) return <div>Загрузка...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Список попыток</h1>
            <ul>
                {attempts.map((attempt) => (
                    <li key={attempt.id}>
                        <Link to={`/attempts/${attempt.id}`}>Попытка ID: {attempt.id}</Link>
                    </li>
                ))}
            </ul>
            <Link to="/attempts/create">Создать новую попытку</Link>
        </div>
    );
};

export default AttemptsList;