import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(sock):
    while True:
        data = sock.recv(1024).decode('utf-8')
        if not data:
            break
        message = json.loads(data)
        handle_message(message)

def handle_message(message):
    if message['type'] == 'file_list':
        print("Files:", message['files'])
    elif message['type'] == 'file_content':
        print(f"Content of {message['filename']}:\n{message['content']}")
    elif message['type'] == 'save':
        print(f"File {message['filename']} has been updated")
    elif message['type'] == 'add':
        print(f"File {message['filename']} has been added")
    elif message['type'] == 'delete':
        print(f"File {message['filename']} has been deleted")

def send_request(sock, request):
    sock.send(json.dumps(request).encode('utf-8'))

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        username = input("Enter your username: ")
        s.send(username.encode('utf-8'))
        
        threading.Thread(target=receive_messages, args=(s,)).start()
        
        while True:
            command = input("Enter command (view/save/add/delete): ")
            if command == 'view':
                filename = input("Enter filename to view: ")
                send_request(s, {'type': 'view', 'filename': filename})
            elif command == 'save':
                filename = input("Enter filename to save: ")
                content = input("Enter new content: ")
                send_request(s, {'type': 'save', 'filename': filename, 'content': content})
            elif command == 'add':
                filename = input("Enter new filename to add: ")
                send_request(s, {'type': 'add', 'filename': filename})
            elif command == 'delete':
                filename = input("Enter filename to delete: ")
                send_request(s, {'type': 'delete', 'filename': filename})

if __name__ == "__main__":
    start_client()
