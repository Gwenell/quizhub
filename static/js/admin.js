function fetchConnectedUsers() {
    fetch('/connected_users')
        .then(response => response.json())
        .then(data => {
            const usersList = document.getElementById('users-list');
            usersList.innerHTML = '';
            if (data.users) {
                data.users.forEach(user => {
                    const userItem = document.createElement('li');
                    userItem.textContent = `${user.pseudo} (${user.page_id})`;
                    usersList.appendChild(userItem);
                });
            }
        });
}

function sendNotification() {
    fetch('/notify', {
        method: 'POST',
    }).then(response => response.text())
      .then(data => {
          document.getElementById('notification-status').innerText = data;
      });
}

setInterval(fetchConnectedUsers, 5000); // Fetch connected users every 5 seconds
document.addEventListener('DOMContentLoaded', fetchConnectedUsers); // Fetch immediately on load
