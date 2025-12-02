
/*1. Grabbing HTML elements
We store references to the input fields and list so we can interact with them easily in JavaScript.*/

const form = document.getElementById('entryForm');
const nameInput = document.getElementById('name');
const messageInput = document.getElementById('message');
const entriesList = document.getElementById('entriesList');

/*2. Loading existing entries
fetch('/api/entries') sends a GET request to the Flask backend.
The backend returns a list of entries (JSON).
Then we call renderEntries() to display them. */

async function loadEntries() {
  const res = await fetch('/api/entries');
  const entries = await res.json();
  renderEntries(entries);
}

/* 3. Rendering entries
Clears the old list.
Loops through the entries returned by the backend.
Creates <li> elements dynamically for each message.
Converts createdAt to a readable date/time. */

function renderEntries(entries) {
  entriesList.innerHTML = '';
  if (!entries.length) {
    entriesList.innerHTML = '<li>No entries yet — be the first!</li>';
    return;
  }
  
  entries.forEach(e => {
    const li = document.createElement('li');
    li.className = 'entry';
    li.innerHTML = `
      <small>${escapeHtml(e.name)} · ${new Date(e.createdAt).toLocaleString()}</small>
      <div>${escapeHtml(e.message)}</div>
    `;
    entriesList.appendChild(li);
  });
}

/*4. Submitting a new entry
When user clicks “Post”, this event runs.
e.preventDefault() stops the form from reloading the page.
We create a JavaScript object (payload) with the form data.*/

form.addEventListener('submit', async e => {
  e.preventDefault();
  const payload = {
    name: nameInput.value.trim(),
    message: messageInput.value.trim()
  };
  if (!payload.message) return alert('Message cannot be empty');

  /*Sends the data to the Flask backend using POST.
    We tell the server that the data is JSON (Content-Type: application/json).*/
  
  const res = await fetch('/api/entries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
 /*If the request succeeds, clear the form and reload the list.
   Otherwise, show an error.*/
  
  if (res.ok) {
    messageInput.value = '';
    nameInput.value = '';
    loadEntries();
  } else {
    const err = await res.json();
    alert(err.error || 'Failed to post');
  }
});

/*Escaping HTML (security)
  Why: Prevents users from injecting harmful HTML or JavaScript (XSS).
  It replaces special characters with safe equivalents.*/

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

/*Run at startup
Loads existing entries from the backend as soon as the page opens.*/

window.addEventListener('load', loadEntries);
