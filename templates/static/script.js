
document.getElementById("questionForm").addEventListener("submit", function (event) {
    event.preventDefault();
    askQuestion();
});

async function askQuestion() {
    const url = document.getElementById("videoUrl").value.trim();
    const question = document.getElementById("question").value.trim();
    const answerBox = document.getElementById("answer");
    const button = document.getElementById("askButton");

    answerBox.textContent = "Loading answer...";
    button.disabled = true;

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: url, question: question })
        });

        const data = await response.json();
        answerBox.textContent = data.answer || "No answer received.";

    } catch (error) {
        answerBox.textContent = "Could not connect to the server.";
        console.error(error);
    } finally {
        button.disabled = false;
    }
}
