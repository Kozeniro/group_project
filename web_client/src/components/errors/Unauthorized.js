import React from 'react';

const Unauthorized = () => (
    <div>
        <h1>401 - Неавторизованный доступ</h1>
        <p>Ваш токен истек или недействителен. Пожалуйста, войдите снова.</p>
        <a href="/" className="link-button">Вернуться на главную</a>
    </div>
);

export default Unauthorized;