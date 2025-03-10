// Only run this code in a browser environment
if (typeof window !== "undefined") {
  document.addEventListener("DOMContentLoaded", function () {
    // Your Diary Notes App JavaScript code goes here
    console.log("Running from app.js");

    let diaryData = {
      subjects: [],
    };

    let currentSubjectId = null;
    let currentSortOrder = "desc";

    // Load data from local storage
    function loadData() {
      const storedData = localStorage.getItem("diaryData");
      if (storedData) {
        diaryData = JSON.parse(storedData);
      }
      renderSubjects();
      // Set the music source after DOM is loaded to ensure the element exists.
      let musicSource = document.getElementById("musicSource");
      if (musicSource) {
        musicSource.src = "audio.mp3";
        let audio = document.getElementById("backgroundMusic");
        if (audio) {
          audio.load(); // Load the new source
          audio.play().catch((error) => {
            console.error("Autoplay prevented or failed: ", error);
          });
        }
      } else {
        console.error("musicSource element not found!");
      }
    }

    // Save data to local storage
    function saveData() {
      localStorage.setItem("diaryData", JSON.stringify(diaryData));
    }

    // Function to generate a unique ID
    function generateId() {
      return (
        Math.random().toString(36).substring(2, 15) +
        Math.random().toString(36).substring(2, 15)
      );
    }

    // Add a new subject
    function addSubject() {
      const subjectName = document
        .getElementById("new-subject-name")
        .value.trim();
      if (subjectName) {
        const newSubject = {
          id: generateId(),
          name: subjectName,
          notes: [],
        };
        diaryData.subjects.push(newSubject);
        saveData();
        renderSubjects();
        document.getElementById("new-subject-name").value = "";
      } else {
        alert("Subject name cannot be empty.");
      }
    }

    // Render the subjects in the table
    function renderSubjects() {
      const subjectTableBody = document.querySelector("#subject-table tbody");
      subjectTableBody.innerHTML = "";

      diaryData.subjects.forEach((subject) => {
        const row = subjectTableBody.insertRow();

        const nameCell = row.insertCell();
        nameCell.textContent = subject.name;

        const actionsCell = row.insertCell();
        actionsCell.classList.add("actions");

        const viewButton = document.createElement("button");
        viewButton.textContent = "View Notes";
        viewButton.onclick = () => showNotes(subject.id);
        actionsCell.appendChild(viewButton);

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.onclick = () => editSubject(subject.id);
        actionsCell.appendChild(editButton);

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.onclick = () => deleteSubject(subject.id);
        actionsCell.appendChild(deleteButton);
      });
    }

    // Edit an existing subject
    function editSubject(subjectId) {
      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );
      if (subject) {
        const newName = prompt("Enter new subject name:", subject.name);
        if (newName !== null && newName.trim() !== "") {
          subject.name = newName.trim();
          saveData();
          renderSubjects();
        }
      }
    }

    // Delete a subject
    function deleteSubject(subjectId) {
      if (confirm("Are you sure you want to delete this subject?")) {
        diaryData.subjects = diaryData.subjects.filter(
          (subject) => subject.id !== subjectId,
        );
        saveData();
        renderSubjects();
        if (currentSubjectId === subjectId) {
          hideNotes();
        }
      }
    }

    // Show notes for a selected subject
    function showNotes(subjectId) {
      currentSubjectId = subjectId;
      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );

      if (subject) {
        document.getElementById("current-subject-name").textContent =
          subject.name;
        document.getElementById("notes-section").style.display = "block";
        renderNotes(subjectId);
      }
    }

    // Hide the notes section
    function hideNotes() {
      document.getElementById("notes-section").style.display = "none";
      currentSubjectId = null;
    }

    // Add a new note to the current subject
    function addNote() {
      if (!currentSubjectId) {
        alert("No subject selected.");
        return;
      }

      const noteText = document.getElementById("new-note-text").value.trim();
      if (noteText) {
        const subject = diaryData.subjects.find(
          (subject) => subject.id === currentSubjectId,
        );
        if (subject) {
          const newNote = {
            id: generateId(),
            text: noteText,
            important: false,
            createdAt: new Date().toISOString(),
          };
          subject.notes.push(newNote);
          saveData();
          renderNotes(currentSubjectId);
          document.getElementById("new-note-text").value = "";
        }
      } else {
        alert("Note text cannot be empty.");
      }
    }

    // Render the notes for the current subject
    function renderNotes(subjectId) {
      const noteTableBody = document.querySelector("#note-table tbody");
      noteTableBody.innerHTML = "";

      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );
      if (subject) {
        // Sort notes based on current sort order
        if (currentSortOrder === "asc") {
          subject.notes.sort(
            (a, b) => new Date(a.createdAt) - new Date(b.createdAt),
          );
        } else {
          subject.notes.sort(
            (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
          );
        }

        subject.notes.forEach((note) => {
          const row = noteTableBody.insertRow();
          row.classList.add("note-row");

          row.addEventListener("click", function () {
            openNotePopup(
              subject.id,
              subject.name,
              note.id,
              note.text,
              new Date(note.createdAt).toLocaleString(),
            );
          });

          const noteCell = row.insertCell();
          noteCell.textContent = note.text;

          const dateCell = row.insertCell();
          dateCell.textContent = new Date(note.createdAt).toLocaleString();

          const importantCell = row.insertCell();
          importantCell.textContent = note.important ? "!" : "";

          const actionsCell = row.insertCell();
          actionsCell.classList.add("actions");

          const editButton = document.createElement("button");
          editButton.textContent = "Edit";
          editButton.onclick = () => editNote(subjectId, note.id);
          actionsCell.appendChild(editButton);

          const deleteButton = document.createElement("button");
          deleteButton.textContent = "Delete";
          deleteButton.onclick = () => deleteNote(subjectId, note.id);
          actionsCell.appendChild(deleteButton);

          const toggleImportantButton = document.createElement("button");
          toggleImportantButton.textContent = note.important
            ? "Unmark"
            : "Mark Important";
          toggleImportantButton.onclick = () =>
            toggleImportant(subjectId, note.id);
          actionsCell.appendChild(toggleImportantButton);
        });
      }
    }

    // Edit an existing note
    function editNote(subjectId, noteId) {
      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );
      if (subject) {
        const note = subject.notes.find((note) => note.id === noteId);
        if (note) {
          const newText = prompt("Enter new note text:", note.text);
          if (newText !== null && newText.trim() !== "") {
            note.text = newText.trim();
            saveData();
            renderNotes(subjectId);
          }
        }
      }
    }

    // Delete a note
    function deleteNote(subjectId, noteId) {
      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );
      if (subject) {
        subject.notes = subject.notes.filter((note) => note.id !== noteId);
        saveData();
        renderNotes(subjectId);
      }
    }

    // Toggle the 'important' status of a note
    function toggleImportant(subjectId, noteId) {
      const subject = diaryData.subjects.find(
        (subject) => subject.id === subjectId,
      );
      if (subject) {
        const note = subject.notes.find((note) => note.id === noteId);
        if (note) {
          note.important = !note.important;
          saveData();
          renderNotes(subjectId);
        }
      }
    }

    // Sort notes alphabetically
    function sortNotes() {
      if (!currentSubjectId) {
        alert("No subject selected.");
        return;
      }

      const subject = diaryData.subjects.find(
        (subject) => subject.id === currentSubjectId,
      );
      if (subject) {
        subject.notes.sort((a, b) => a.text.localeCompare(b.text));
        saveData();
        renderNotes(currentSubjectId);
      }
    }

    // Sort notes chronologically
    function sortNotesChronologically() {
      if (!currentSubjectId) {
        alert("No subject selected.");
        return;
      }
      // Toggle sort order
      currentSortOrder = currentSortOrder === "asc" ? "desc" : "asc";
      renderNotes(currentSubjectId);
    }

    // Search function
    function search() {
      const searchTerm = document
        .getElementById("search-input")
        .value.toLowerCase();
      const searchResults = [];

      diaryData.subjects.forEach((subject) => {
        if (subject.name.toLowerCase().includes(searchTerm)) {
          searchResults.push({
            type: "subject",
            subjectId: subject.id,
            name: subject.name,
            content: subject.name,
          });
        }

        subject.notes.forEach((note) => {
          if (note.text.toLowerCase().includes(searchTerm)) {
            searchResults.push({
              type: "note",
              subjectId: subject.id,
              noteId: note.id,
              name: subject.name,
              content: note.text,
            });
          }
        });
      });

      displaySearchResults(searchResults);
    }

    // Display search results in the table
    function displaySearchResults(results) {
      const subjectTableBody = document.querySelector("#subject-table tbody");
      subjectTableBody.innerHTML = "";

      if (results.length === 0) {
        const noResultsRow = subjectTableBody.insertRow();
        const noResultsCell = noResultsRow.insertCell();
        noResultsCell.textContent = "No search results found.";
        noResultsCell.colSpan = 2;
      } else {
        results.forEach((result) => {
          const row = subjectTableBody.insertRow();

          const nameCell = row.insertCell();
          nameCell.textContent =
            result.type === "subject"
              ? `Subject: ${result.content}`
              : `Note in ${result.name}: ${result.content}`;

          const actionsCell = row.insertCell();
          actionsCell.classList.add("actions");

          const viewButton = document.createElement("button");
          viewButton.textContent = "View";
          viewButton.onclick = () => {
            if (result.type === "subject") {
              showNotes(result.subjectId);
            } else {
              showNotes(result.subjectId);
            }
          };
          actionsCell.appendChild(viewButton);
        });
      }
    }

    // --- Popup Functions ---
    function openNotePopup(
      subjectId,
      subjectName,
      noteId,
      noteText,
      noteDateTime,
    ) {
      document.getElementById("popup-subject-name").textContent =
        `Subject: ${subjectName}`;
      document.getElementById("popup-note-text").textContent = noteText;
      document.getElementById("popup-note-datetime").textContent = noteDateTime;

      document.getElementById("popup-subject-id").value = subjectId;
      document.getElementById("popup-note-id").value = noteId;

      document.getElementById("note-popup-overlay").style.display = "flex";

      // Apply animations to popup content
      document.getElementById("popup-subject-name").style.animation =
        `subtlePulse 7s infinite alternate`;
      document.getElementById("popup-note-text").style.animation =
        `subtleZoom 3s ease-in-out`;
      document.getElementById("popup-note-datetime").style.animation =
        `gentleHueRotate 12s infinite linear`;
    }

    function closeNotePopup() {
      document.getElementById("note-popup-overlay").style.display = "none";
    }

    function editNoteInPopup() {
      const subjectId = document.getElementById("popup-subject-id").value;
      const noteId = document.getElementById("popup-note-id").value;
      editNote(subjectId, noteId);
      closeNotePopup();
    }

    function deleteNoteInPopup() {
      const subjectId = document.getElementById("popup-subject-id").value;
      const noteId = document.getElementById("popup-note-id").value;
      deleteNote(subjectId, noteId);
      closeNotePopup();
    }

    function toggleImportantInPopup() {
      const subjectId = document.getElementById("popup-subject-id").value;
      const noteId = document.getElementById("popup-note-id").value;
      toggleImportant(subjectId, noteId);
      closeNotePopup();
    }

    // Initial load
    loadData();
  });
} else {
  console.log(
    "This script is running in a Node.js environment where document is not available",
  );
}
