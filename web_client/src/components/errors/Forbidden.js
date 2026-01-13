import React from 'react';

const Forbidden = () => (
    <div>
        <h1>403 - Доступ запрещен</h1>
        <p>У вас нет прав для выполнения этого действия.</p>
        <a href="/" className="link-button">Вернуться на главную</a>
    </div>
);

export default Forbidden;