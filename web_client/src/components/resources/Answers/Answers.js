import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AnswersList from './AnswersList';
import AnswerDetail from './AnswerDetail';

const Answers = () => {
    return (
        <Routes>
            {/* Список ответов */}
            <Route path="/" element={<AnswersList />} />

            {/* Детали ответа */}
            <Route path="/:id" element={<AnswerDetail />} />
        </Routes>
    );
};

export default Answers;