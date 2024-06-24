document.addEventListener('DOMContentLoaded', function() {
    const questionTypeSelect = document.querySelector('select[name="type"]');
    const answersContainer = document.querySelector('.answers-container');

    function updateAnswerFields() {
        const isMultipleChoice = questionTypeSelect.value === 'multiple';
        answersContainer.innerHTML = '';

        if (questionTypeSelect.value === 'boolean') {
            answersContainer.innerHTML = `
                <div>
                    <input type="checkbox" name="correct_1" id="correct_1" class="boolean-correct"> True
                </div>
                <div>
                    <input type="checkbox" name="correct_2" id="correct_2" class="boolean-correct"> False
                </div>
            `;

            document.querySelectorAll('.boolean-correct').forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    if (this.checked) {
                        document.querySelectorAll('.boolean-correct').forEach(box => {
                            if (box !== this) box.checked = false;
                        });
                    }
                });
            });
        } else {
            answersContainer.innerHTML = `
                <div class="answer-row">
                    <div class="answer-item">
                        <input type="text" name="answers-0" placeholder="Answer 1">
                        <input type="checkbox" name="correct_0">
                    </div>
                    <div class="answer-item">
                        <input type="text" name="answers-1" placeholder="Answer 2">
                        <input type="checkbox" name="correct_1">
                    </div>
                </div>
                <div class="answer-row">
                    <div class="answer-item">
                        <input type="text" name="answers-2" placeholder="Answer 3">
                        <input type="checkbox" name="correct_2">
                    </div>
                    <div class="answer-item">
                        <input type="text" name="answers-3" placeholder="Answer 4">
                        <input type="checkbox" name="correct_3">
                    </div>
                </div>
            `;
        }
    }

    questionTypeSelect.addEventListener('change', updateAnswerFields);
    updateAnswerFields();  // Call once on load to set the initial state
});