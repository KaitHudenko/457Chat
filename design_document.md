## ✅ Client-Side Requirements

### 📋 Basic Functionality
- The client must:
  - Connect to the server via **TCP socket** (no SocketIO or WebSocket libraries).
  - Prompt the user to **enter a username** at startup.
  - Prepend that username to every message sent to the server.

### 🧵 Threading
- Use a **dedicated thread** to:
  - Listen for and receive messages from the server.
  - Prevent incoming messages from interfering with message typing or UI.

### 💬 UI Requirements
- The client must include a **User Interface (UI)**, either text-based (TUI) or graphical (GUI):
  - Clearly separate the **input area** from the **conversation display area**.
  - Allow the input area to support at least **two lines** of text.
  - Automatically **clear the input box** when a message is sent.
  - Automatically **scroll the chat history up** as new messages arrive.
  - Incoming messages must **not overwrite or mix with** the message currently being typed.

### 📦 Message Handling
- Messages must be:
  - **Sent** to the server including the sender's name.
  - **Received** from the server and **displayed immediately** to the user via the UI.
- Incoming messages must **update the conversation area independently** from the typing input.
  - This requires the receiving thread to **push messages to a queue** (or similar structure), and the UI thread to periodically **poll and display** those messages.

### ❌ No Persistent History
- The client should not expect any chat history upon connecting.
  - It will only receive messages **after it joins** the chat session.

### 🛑 Graceful Shutdown
- If the **client disconnects**, it must cleanly:
  - Close the socket.
  - Terminate all background threads.
- If the **server crashes or terminates**, the client must:
  - Detect this and **terminate gracefully**, showing a message to the user.

---

## ⭐ Extra Credit (Optional Features)

### ✨ Improved UI (1–4 pts)
- Additional visual enhancements (e.g., color-coding messages, resizing windows, responsive layout).

### 🔗 URL Recognition (3 pts)
- Detect URLs in messages and make them **clickable links**.

### 😀 Emoji Shortcuts (3–5 pts)
- Recognize emoji text codes like `:thumbsup:` and replace with Unicode (👍).
- Bonus: Show emojis **live as the user types**, not just after sending.

### 📩 Direct Messaging (3 pts)
- Support direct messages to specific users via `@username` syntax.

---

## ⚙️ Other Notes
- The UI framework **must not allow updates to the UI from non-UI threads**.
  - To work around this, use a shared **thread-safe queue**.
  - UI should poll the queue periodically (e.g., every 100ms) to process updates.

- You may use:
  - `Tkinter` or `PyQt` for GUI
  - `curses` or similar for TUI
  - `queue.Queue` for safe communication between threads
