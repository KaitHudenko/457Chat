import tkinter as tk
from tkinter import scrolledtext, Text, END
import hashlib

class ChatUI:
    def __init__(self, username, message_queue, send_callback, on_close):
        self.username = username
        self.message_queue = message_queue
        self.send_callback = send_callback
        self.on_close = on_close

        self.root = tk.Tk()
        self.root.title(f"Chat - {self.username}")
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # === Chat display area ===
        self.chat_display = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD, height=20)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.tag_config('default', foreground='black')
        
        # === Message input area ===
        self.input_text = tk.Text(self.root, height=2, wrap=tk.WORD)
        self.input_text.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.input_text.bind("<Return>", self.send_message_event)
        self.input_text.bind("<Shift-Return>", self.newline_event)

        # === Send button ===
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

        # === Start UI update loop ===
        self.update_chat_display()

    def send_message_event(self, event):
        self.send_message()
        return "break"  # Prevents newline on Enter key

    def newline_event(self, event):
        self.input_text.insert(tk.END, "\n")
        return "break"  # Allows Shift+Enter for new lines

    def send_message(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if user_input:
            self.send_callback(user_input)
            self.input_text.delete("1.0", tk.END)

    def update_chat_display(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.chat_display.configure(state='normal')
            insert_colored_message(self.chat_display, message)
            self.chat_display.configure(state='disabled')
            self.chat_display.yview(tk.END)  # Auto-scroll

        self.root.after(100, self.update_chat_display)

    def close_window(self):
        self.on_close()

    def run(self):
        self.root.mainloop()

def get_username_color(username):
        """Generate a color hex code based on the username hash."""
        hash_digest = hashlib.md5(username.encode()).hexdigest()
        r = int(hash_digest[0:2], 16)
        g = int(hash_digest[2:4], 16)
        b = int(hash_digest[4:6], 16)
        return f'#{r:02x}{g:02x}{b:02x}'
    
def insert_colored_message(chat_display, message):
        """
        Inserts a chat message into the chat display with colored username if possible.
        """
        chat_display.configure(state='normal')

        if message.startswith('['):
            end_bracket = message.find(']')
            if end_bracket != -1:
                sender = message[1:end_bracket]
                color = get_username_color(sender)

                chat_display.insert(tk.END, '[', 'default')
                chat_display.insert(tk.END, sender, sender)
                chat_display.insert(tk.END, f"] {message[end_bracket+2:]}\n", 'default')
                chat_display.tag_config(sender, foreground=color)
                chat_display.configure(state='disabled')
                chat_display.yview(tk.END)
                return

        # Fallback: insert plain message
        chat_display.insert(tk.END, message + '\n')
        chat_display.configure(state='disabled')
        chat_display.yview(tk.END)