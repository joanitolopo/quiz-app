var correctAnswer = question.correct_options[0]-1;  // Access the correct_answer property from the global question object
var numCorrect = 0;
var numWrong = 0;

function loadNextQuestion() {
    location.reload();
}

function selectOption(button, selectedOption) {
    var isCorrect = selectedOption === question.options[correctAnswer];
    if (isCorrect) {
        button.classList.remove("btn-outline-primary");
        button.classList.add("btn-success");
        numCorrect++;
    } else {
        button.classList.remove("btn-outline-primary");
        button.classList.add("btn-danger");
        numWrong++;
    }

    // Disable further clicks on options
    var buttons = document.querySelectorAll('.btn-block');
    buttons.forEach(function(btn) {
        btn.disabled = true;
    });

    var postData = {
        "selected_option": selectedOption,
        "is_correct": isCorrect
    }

    fetch("/quiz_result", {
        method: "POST",
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}


