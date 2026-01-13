// src/components/resources/Tests/TestEdit.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchTestDetails, updateTest } from './TestAPI';

const TestEdit = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadTestDetails = async () => {
            setLoading(true);
            try {
                const response = await fetchTestDetails(id);
                setName(response.data.name);
                setDescription(response.data.description);
            } catch (error) {
                console.error('Ошибка при загрузке данных теста:', error);
            } finally {
                setLoading(false);
            }
        };

        loadTestDetails();
    }, [id]);

    const handleSave = async () => {
        try {
            await updateTest(id, { name, description });
            navigate(`/tests/${id}`);
        } catch (error) {
            console.error('Ошибка при сохранении данных теста:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div>
            <h1>Редактирование теста</h1>
            <div>
                <label>Название:</label>
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
            </div>
            <div>
                <label>Описание:</label>
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
            </div>
            <button onClick={handleSave}>Сохранить</button>
        </div>
    );
};

export default TestEdit;