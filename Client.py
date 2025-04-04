import socket
import threading
import queue
import sys
from UI import ChatUI
# from emojis import replace_emojis  # Optional: if implementing emoji feature

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def receive_messages(client_sock, message_queue, stop_event):
    """
    Thread to receive messages from the server and push them into the message queue.
    """
    try:
        while not stop_event.is_set():
            data = client_sock.recv(1024)
            if not data:
                message_queue.put("[System] Server connection closed.")
                stop_event.set()
                break
            message = data.decode()
            message_queue.put(message)
    except Exception as e:
        message_queue.put(f"[Error] {e}")
        stop_event.set()

def main():
    # Connect to Server
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"Could not connect to server: {e}")
        sys.exit(1)

    # Get Username
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty.")
        sys.exit(1)

    # Set up Queue and Thread for Incoming Messages
    message_queue = queue.Queue()
    stop_event = threading.Event()
    client_thread = threading.Thread(target=receive_messages, args=(client_sock, message_queue, stop_event), daemon=True)
    client_thread.start()

    # Launch UI
    def send_callback(user_input):
        message = f"[{username}] {user_input}"
        # message = replace_emojis(message)  # Optional
        try:
            client_sock.sendall(message.encode())
        except Exception as e:
            message_queue.put(f"[Error] Failed to send: {e}")
            stop_event.set()

    def on_close():
        stop_event.set()
        client_sock.close()
        sys.exit(0)

    chat_ui = ChatUI(username=username, message_queue=message_queue, send_callback=send_callback, on_close=on_close)
    chat_ui.run()

if __name__ == "__main__":
    main()
