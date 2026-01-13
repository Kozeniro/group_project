import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createDiscipline } from './DisciplineAPI';

const DisciplineCreate = () => {
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState(null); 

    const handleCreate = async () => {
        try {
            const response = await createDiscipline({ name, description });
            console.log('Response from creating discipline:', response.data); 
            navigate('/disciplines'); // Перенаправляем на страницу дисциплин
        } catch (error) {
            console.error('Ошибка при создании дисциплины:', error);
            setError('Не удалось создать дисциплину.'); 
        }
    };

    return (
        <div>
            <h1>Создание дисциплины</h1>
            {error && <div style={{ color: 'red' }}>{error}</div>} {/* Отображаем сообщение об ошибке */}
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
            <button onClick={handleCreate}>Создать</button>
        </div>
    );
};

export default DisciplineCreate;