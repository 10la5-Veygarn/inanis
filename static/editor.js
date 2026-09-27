// This is a display-only convenience — the word count and reading time
// used for saving, statistics, etc. are always computed server-side by
// Document.word_counter(). This just keeps the on-screen number moving
// while the user types, without a round trip on every keystroke.

const textarea = document.getElementById("content");
const wordCountEl = document.getElementById("word-count");
const readingTimeEl = document.getElementById("reading-time");
const saveHint = document.getElementById("save-hint");

const WORDS_PER_MINUTE = 200;

function countWords(text) {
    const matches = text.match(/\b\w+(?:['\-.]\w+)*\b/g);
    return matches ? matches.length : 0;
}

function updateStats() {
    const count = countWords(textarea.value);
    wordCountEl.textContent = count;
    readingTimeEl.textContent = (count / WORDS_PER_MINUTE).toFixed(1);
}

textarea.addEventListener("input", () => {
    updateStats();
    saveHint.textContent = "Unsaved changes";
});

document.getElementById("save-form").addEventListener("submit", () => {
    saveHint.textContent = "Saving…";
});

updateStats();
