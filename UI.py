import tkinter as tk
from tkinter import scrolledtext, Text, messagebox, END
import hashlib
import re
import webbrowser

class ChatUI:
    def __init__(self, username, message_queue, send_callback, on_close):
        self.emoji_dict = {
            ":smile:": "😊",
            ":laugh:": "😂",
            ":thumbsup:": "👍",
            ":heart:": "❤️",
            ":sad:": "😢",
            ":angry:": "😡",
            ":sparkles:": "✨",
            ":rocket:": "🚀"
        }

        self.username = username
        self.message_queue = message_queue
        self.send_callback = send_callback
        self.on_close = on_close

        self.root = tk.Tk()
        self.root.title(f"Chat - {self.username}")
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # === Chat display area ===
        emoji_font = ("Segoe UI Emoji", 12)
        self.chat_display = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD, height=20, font=emoji_font)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.tag_config('default', foreground='black')
        self.chat_display.tag_config('link', foreground='blue', underline=True)
        self.chat_display.tag_config('dm', foreground='purple')
        self.chat_display.tag_config('sent_msg', foreground='white', background='green4')
        self.chat_display.tag_config('recv_msg', foreground='blue4')

        # === Message input area ===
        self.input_text = tk.Text(self.root, height=2, wrap=tk.WORD)
        self.input_text.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.input_text.bind("<Return>", self.send_message_event)
        self.input_text.bind("<Shift-Return>", self.newline_event)

        # === Send button ===
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

        # === Emoji Button ===
        emoji_button = tk.Button(self.root, text="😊", command=self.emoji_show)
        emoji_button.pack(side=tk.RIGHT, padx=5)

        # === Start UI update loop ===
        self.update_chat_display()

    def emoji_show(self):
        emojis = list(self.emoji_dict.values())

        emojiSel = tk.Toplevel(self.root)
        emojiSel.title("Emoji Picker")
        # Set size
        emojiSel.geometry("350x150") 
        emojiSel.resizable(False, False)

        # Create a frame to hold the emoji buttons
        frame = tk.Frame(emojiSel)
        frame.pack(pady=5, padx=5)

        # Alignment
        cols = 4  
        for i, emoji in enumerate(emojis):
            row = i // cols  
            col = i % cols  
            btn = tk.Button(frame, text=emoji, font=("Segoe UI Emoji", 14),
                            command=lambda e=emoji: self.emoji_enter(e),
                            width=2, height=1)
            btn.grid(row=row, column=col, padx=2, pady=2)

        emojiSel.transient(self.root) 
        emojiSel.grab_set() 

    def emoji_enter(self, emoji):
        self.input_text.insert(tk.END, emoji)
        self.input_text.focus()

    def text_to_emoji(self, msg):
        for shortcut, emoji in self.emoji_dict.items():
            msg = msg.replace(shortcut, emoji)
        return msg

    def send_message_event(self, event):
        self.send_message()
        return "break"  # Prevents newline on Enter key

    def newline_event(self, event):
        self.input_text.insert(tk.END, "\n")
        return "break"  # Allows Shift+Enter for new lines

    def send_message(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if user_input:
            user_input = self.text_to_emoji(user_input)
            self.send_callback(user_input)
            self.input_text.delete("1.0", tk.END)

    def update_chat_display(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.display_message(message)
            self.chat_display.yview(tk.END)  # Auto-scroll

        self.root.after(100, self.update_chat_display)

    def display_message(self, message):
        self.chat_display.config(state='normal')

        tag = 'recv_msg'
        sender = None
        content = message

        # Check for DM
        if message.startswith("DM:"):
            parts = message.split(":", 3)
            if len(parts) >= 4:
                _, recipient, sender, content = parts
                tag = 'dm'
                message = f"{sender} (DM): {content}"

        # Check for formatted username
        elif message.startswith("["):
            end_bracket = message.find("]")
            if end_bracket != -1:
                sender = message[1:end_bracket]
                color = get_username_color(sender)
                self.chat_display.tag_config(sender, foreground=color)

                # Insert sender name in color
                self.chat_display.insert(tk.END, '[', 'default')
                self.chat_display.insert(tk.END, sender, sender)
                self.chat_display.insert(tk.END, '] ', 'default')

                # Cut message content for link insertion
                message_body = message[end_bracket + 2:]
                insert_links(self.chat_display, message_body, tag=tag)

                self.chat_display.insert(tk.END, "\n", tag)
                self.chat_display.config(state='disabled')
                self.chat_display.yview(tk.END)
                return

        # Fallback: full message with links
        insert_links(self.chat_display, message, tag=tag)
        self.chat_display.insert(tk.END, "\n", tag)

        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def close_window(self):
        self.on_close()

    def run(self):
        self.root.mainloop()

def insert_links(text_widget, message, tag="default"):
    url_pattern = r"(?:https?://[^\s,]+|www\.[^\s,]+)"
    split_pattern = f"({url_pattern})"  # for clarity
    parts = re.split(split_pattern, message)
    
    for part in parts:
        if re.match(url_pattern, part):
            unique_tag = f"url_{hash(part)}_{text_widget.index(tk.END)}"
            text_widget.insert(tk.END, part, (unique_tag,))
            text_widget.tag_config(unique_tag, foreground="blue", underline=True)
            text_widget.tag_bind(unique_tag, "<Button-1>", lambda e, u=part: open_url(u))
        else:
            text_widget.insert(tk.END, part, tag)


def open_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    webbrowser.open(url)

def get_username_color(username):
    hash_digest = hashlib.md5(username.encode()).hexdigest()
    r = int(hash_digest[0:2], 16)
    g = int(hash_digest[2:4], 16)
    b = int(hash_digest[4:6], 16)
    return f'#{r:02x}{g:02x}{b:02x}'
    