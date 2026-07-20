const storageKey = "ai-lab-notes";

const noteForm = document.querySelector("#note-form");
const experimentInput = document.querySelector("#experiment");
const resultInput = document.querySelector("#result");
const notesList = document.querySelector("#notes-list");
const clearButton = document.querySelector("#clear-notes");
const formMessage = document.querySelector("#form-message");

function loadNotes() {
  const savedNotes = localStorage.getItem(storageKey);

  if (!savedNotes) {
    return [];
  }

  try {
    return JSON.parse(savedNotes);
  } catch {
    // If stored data is damaged, start with an empty list.
    return [];
  }
}

function saveNotes(notes) {
  localStorage.setItem(storageKey, JSON.stringify(notes));
}

function renderNotes() {
  const notes = loadNotes();
  notesList.replaceChildren();

  if (notes.length === 0) {
    const emptyMessage = document.createElement("p");
    emptyMessage.className = "empty-state";
    emptyMessage.textContent = "No notes saved yet.";
    notesList.append(emptyMessage);
    return;
  }

  notes.forEach((note) => {
    const article = document.createElement("article");
    article.className = "note";

    const title = document.createElement("h4");
    title.textContent = note.experiment;

    const result = document.createElement("p");
    result.textContent = note.result;

    const date = document.createElement("time");
    date.dateTime = note.createdAt;
    date.textContent = `Saved ${new Date(note.createdAt).toLocaleString()}`;

    article.append(title, result, date);
    notesList.append(article);
  });
}

noteForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const notes = loadNotes();
  const newNote = {
    experiment: experimentInput.value.trim(),
    result: resultInput.value.trim(),
    createdAt: new Date().toISOString(),
  };

  if (!newNote.experiment || !newNote.result) {
    formMessage.textContent = "Please complete both fields.";
    return;
  }

  notes.unshift(newNote);
  saveNotes(notes);
  noteForm.reset();
  formMessage.textContent = "Note saved in this browser.";
  renderNotes();
  experimentInput.focus();
});

clearButton.addEventListener("click", () => {
  localStorage.removeItem(storageKey);
  formMessage.textContent = "All saved notes were cleared.";
  renderNotes();
});

renderNotes();
