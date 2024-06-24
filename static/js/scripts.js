document.addEventListener('DOMContentLoaded', function() {
    const questionTypeSelect = document.querySelector('select[name="type"]');
    const answersContainer = document.querySelector('.answers-container');

    function updateAnswerFields() {
        const answers = answersContainer.querySelectorAll('.form-group');
        const isMultipleChoice = questionTypeSelect.value === 'multiple';
        answers.forEach((answer, index) => {
            const input = answer.querySelector('input[type="checkbox"]');
            if (isMultipleChoice) {
                input.removeAttribute('disabled');
            } else {
                input.setAttribute('disabled', 'disabled');
                input.checked = index === 0;
            }
        });
    }

    questionTypeSelect.addEventListener('change', updateAnswerFields);
    updateAnswerFields();  // Call once on load to set the initial state
});
