document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-question').addEventListener('click', function() {
        const questionsList = document.getElementById('questions-list');
        const newQuestionId = `new-${Date.now()}`;
        const newQuestionItem = document.createElement('li');
        newQuestionItem.innerHTML = `
            <input type="text" name="question-${newQuestionId}" placeholder="New question">
            <a href="#" class="delete-question" data-question-id="${newQuestionId}">Delete</a>
        `;
        questionsList.appendChild(newQuestionItem);
    });

    document.getElementById('questions-list').addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-question')) {
            event.preventDefault();
            const questionId = event.target.getAttribute('data-question-id');
            if (confirm('Are you sure you want to delete this question?')) {
                if (questionId.startsWith('new-')) {
                    event.target.parentElement.remove();
                } else {
                    fetch(`/delete_question/${questionId}`, { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                event.target.parentElement.remove();
                            } else {
                                alert('Failed to delete question');
                            }
                        });
                }
            }
        }
    });

    document.getElementById('delete-quiz').addEventListener('click', function(event) {
        event.preventDefault();
        if (confirm('Are you sure you want to delete this quiz?')) {
            fetch(`/delete_quiz/${quizId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/manage_quizzes';
                    } else {
                        alert('Failed to delete quiz');
                    }
                });
        }
    });
});
