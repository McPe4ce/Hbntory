/* Sends the question to the backoffice and shows the answer on the page. */

const API_URL = "http://localhost:5000/api/query";

const form = document.getElementById("ask-form");
const input = document.getElementById("question");
const button = document.getElementById("submit");
const conversation = document.getElementById("conversation");

/* Adds a message in the conversation and returns it. */
function addMessage(text, kind) {
  const paragraph = document.createElement("p");
  paragraph.className = "message message-" + kind;
  paragraph.textContent = text;

  conversation.appendChild(paragraph);
  conversation.scrollTop = conversation.scrollHeight;

  return paragraph;
}

form.addEventListener("submit", function (event) {
  event.preventDefault();

  const question = input.value.trim();
  if (question === "") {
    return;
  }

  addMessage(question, "user");
  input.value = "";
  button.disabled = true;

  // Waiting message, we remove it when the answer arrives.
  const waiting = addMessage("Searching...", "waiting");

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question }),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      waiting.remove();
      if (data.error) {
        addMessage(data.error, "error");
      } else {
        addMessage(data.answer, "bot");
      }
    })
    .catch(function () {
      waiting.remove();
      addMessage("The service does not answer. Please try again later.", "error");
    })
    .finally(function () {
      button.disabled = false;
      input.focus();
    });
});

/* Clicking an example puts it in the input and sends it. */
const examples = document.querySelectorAll(".example");

examples.forEach(function (example) {
  example.addEventListener("click", function () {
    input.value = example.textContent;
    form.requestSubmit();
  });
});
