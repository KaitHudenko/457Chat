import socket
import threading
from socket import SOL_SOCKET, SO_REUSEADDR

# === Config ===
HOST = '0.0.0.0'        # Accept connections on all interfaces
PORT = 5000             # Match this with client.py
MAX_CONNECTIONS = 20

clients = []
usernames = {}  # socket -> username
clients_lock = threading.Lock()
running = True

def broadcast(message, sender_socket):
    with clients_lock:
        for client in clients[:]:
            try:
                client.sendall(message)
            except:
                # Drop client if failed to send
                clients.remove(client)
                client.close()
                usernames.pop(client, None)

def send_dm(recipient_name, sender_name, content, sender_socket):
    message = f"DM:{recipient_name}:{sender_name}:{content}".encode()
    sent = False

    with clients_lock:
        for client, username in usernames.items():
            if username == recipient_name:
                try:
                    client.sendall(message)
                    sent = True
                    break
                except:
                    clients.remove(client)
                    client.close()
                    usernames.pop(client, None)
                    break

    if not sent:
        try:
            sender_socket.sendall(f"[Server] User '{recipient_name}' not found.".encode())
        except:
            pass

def handle_client(client_socket, client_address):
    print(f"[+] Connected: {client_address}")
    try:
        # First message = username
        username = client_socket.recv(1024).decode().strip()
        if not username:
            raise ValueError("Empty username")

        with clients_lock:
            clients.append(client_socket)
            usernames[client_socket] = username

        while True:
            message = client_socket.recv(1024)
            if not message:
                break

            decoded = message.decode()

            if decoded.startswith("DM:"):
                try:
                    _, recipient, sender, content = decoded.split(":", 3)
                    send_dm(recipient, sender, content, client_socket)
                except ValueError:
                    client_socket.sendall(b"[Server] Invalid DM format.")
            else:
                broadcast(message, sender_socket=client_socket)

    except Exception as e:
        print(f"[!] Error with {client_address}: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
            usernames.pop(client_socket, None)
        client_socket.close()
        print(f"[-] Disconnected: {client_address}")


def server_loop(server_socket):
    global running
    server_socket.settimeout(1.0)  # Allow loop to check 'running' flag
    print(f"[*] Server listening on {HOST}:{PORT} - press enter to quit.")

    while running:
        try:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[!] Accept error: {e}")
            break

def main():
    global running

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CONNECTIONS)

    server_thread = threading.Thread(target=server_loop, args=(server_socket,))
    server_thread.start()

    try:
        input("")  # Press Enter to quit
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C received. Shutting down...")

    print("[*] Shutting down server...")
    running = False

    # Dummy socket to unblock accept
    try:
        dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy.connect(('127.0.0.1', PORT))
        dummy.close()
    except:
        pass

    server_socket.close()
    with clients_lock:
        for client in clients:
            client.close()
        clients.clear()
        usernames.clear()

    server_thread.join()
    print("[*] Server stopped cleanly.")

if __name__ == "__main__":
    main()
