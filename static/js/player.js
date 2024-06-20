document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    socket.on('notification', function(data) {
        const pageId = "{{ page_id }}";
        if (data.page_id === pageId) {
            document.getElementById('notifications').innerText = data.notification;
        }
    });

    socket.on('start_quiz', function(data) {
        // Logic to handle quiz start
    });
});
