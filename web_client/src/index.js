// src/index.js
import React from 'react';
import { createRoot } from 'react-dom/client'; // Импортируем createRoot
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container); // Создаем корень
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);