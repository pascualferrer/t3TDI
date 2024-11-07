function suggestQuestion(movie) {
    const questions = [
        `¿De qué trata ${movie}?`,
        `¿Cómo termina ${movie}?`,
        `¿Cuáles son los personajes principales de ${movie}?`,
        `¿Qué sucede en la primera escena de ${movie}?`
    ];
    const randomQuestion = questions[Math.floor(Math.random() * questions.length)];
    document.getElementById('user-input').value = randomQuestion;
    document.getElementById('user-input').focus();
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const message = userInput.value.trim();

    if (message === '') return;

    const userDiv = document.createElement('div');
    userDiv.className = 'text-end';
    userDiv.innerHTML = `<div class="chat-message">${message}</div>`;
    chatMessages.appendChild(userDiv);
    
    const spinnerDiv = document.createElement('div');
    spinnerDiv.className = 'message-spinner';
    spinnerDiv.innerHTML = `
        <div class="d-flex align-items-center justify-content-center">
            <div class="spinner-border text-primary me-2" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <div>
                <div class="fw-bold">Generando respuesta...</div>
                <small class="text-muted">Esto puede tomar varios segundos</small>
            </div>
        </div>
    `;
    chatMessages.appendChild(spinnerDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    userInput.disabled = true;

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        spinnerDiv.remove();
        const botDiv = document.createElement('div');
        botDiv.className = 'text-start';
        botDiv.innerHTML = `<div class="chat-message">${data.message}</div>`;
        chatMessages.appendChild(botDiv);
    })
    .catch(error => {
        console.error('Error:', error);
        spinnerDiv.remove();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-center';
        errorDiv.innerHTML = `
            <div class="system-message text-danger">
                <i class='bx bx-error-circle'></i> 
                Error: No se pudo obtener respuesta. Por favor, intenta de nuevo.
            </div>
        `;
        chatMessages.appendChild(errorDiv);
    })
    .finally(() => {
        userInput.disabled = false;
        userInput.value = '';
        userInput.focus();
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}