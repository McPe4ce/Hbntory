/* Sends the question to the backoffice and shows the answer on the page.
 *
 * The page is served by nginx on :8080 while the API runs on :5000, so the two
 * are different origins. The call is cross-origin by design: the backend sets
 * the CORS headers and answers the OPTIONS preflight.
 *
 * Every failure below is caught and named, because fetch does not reject on a
 * 404 or a 500 — only on a network-level failure.
 */

const API_URL = "http://localhost:5000/api/query";
const TIMEOUT_MS = 30000;

const MESSAGES = {
  offline: "The service does not answer. Check that it is running.",
  timeout: "The answer is taking too long. Please try again.",
  refused: "The question was refused by the service.",
  failed: "The service ran into an error.",
  unexpected: "Unexpected answer from the service.",
  waiting: "Searching...",
};

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

/* Sends one question and returns the answer.
   Every failure leaves here as an Error carrying the message to display. */
async function ask(question) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response;

  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
      signal: controller.signal,
    });
  } catch (error) {
    // Two different failures arrive here, and only here.
    // AbortError: our own timeout fired. TypeError: the request never left —
    // the service is down, or the origin was refused. The browser keeps the
    // real reason for the console, so these two look identical from here.
    throw new Error(error.name === "AbortError" ? MESSAGES.timeout : MESSAGES.offline);
  } finally {
    clearTimeout(timer);
  }

  // Read the body first, whatever the status: the backend explains a 400 or a
  // 503 in its own words ("Your question is too long", "The catalog is not
  // available right now"), and that message beats anything written here.
  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  const serverMessage = data && typeof data.error === "string" ? data.error : null;

  // fetch resolves on a 404 and on a 500, so the status is tested by hand.
  if (!response.ok) {
    const fallback = response.status < 500 ? MESSAGES.refused : MESSAGES.failed;
    throw new Error(serverMessage || fallback);
  }

  // A 200 carrying the wrong shape is still an unusable answer.
  if (!data || typeof data.answer !== "string") {
    throw new Error(serverMessage || MESSAGES.unexpected);
  }

  return data.answer;
}

form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const question = input.value.trim();
  if (question === "") {
    return;
  }

  addMessage(question, "user");
  input.value = "";

  // Disabled until the answer arrives: a second click would send a second
  // question, and nothing guarantees the order the two answers come back in.
  button.disabled = true;

  const waiting = addMessage(MESSAGES.waiting, "waiting");

  try {
    const answer = await ask(question);
    waiting.remove();
    addMessage(answer, "bot");
  } catch (error) {
    waiting.remove();
    addMessage(error.message, "error");
  } finally {
    button.disabled = false;
    input.focus();
  }
});

/* Clicking an example puts it in the input and sends it. */
const examples = document.querySelectorAll(".example");

examples.forEach(function (example) {
  example.addEventListener("click", function () {
    input.value = example.textContent;
    form.requestSubmit();
  });
});
