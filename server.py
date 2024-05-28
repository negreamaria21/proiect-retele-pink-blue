import socket
import threading
import os
import json

HOST = '127.0.0.1'
PORT = 65432
DIRECTORY = 'files/'

clients = {}
files_in_edit = {}

def handle_client(conn, addr):
    print(f'Connected by {addr}')
    user = conn.recv(1024).decode('utf-8')
    clients[conn] = user
    send_file_list(conn)
    
    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break
        request = json.loads(data)
        handle_request(conn, request)
    
    del clients[conn]
    conn.close()

def handle_request(conn, request):
    if request['type'] == 'view':
        send_file_content(conn, request['filename'])
    elif request['type'] == 'edit':
        handle_edit_request(conn, request['filename'])
    elif request['type'] == 'save':
        save_file_content(conn, request['filename'], request['content'])
    elif request['type'] == 'release':
        release_file(conn, request['filename'])
    elif request['type'] == 'add':
        add_file(request['filename'])
    elif request['type'] == 'delete':
        delete_file(request['filename'])

def send_file_list(conn):
    files = os.listdir(DIRECTORY)
    file_list = [{'filename': f, 'editor': files_in_edit.get(f)} for f in files]
    conn.send(json.dumps({'type': 'file_list', 'files': file_list}).encode('utf-8'))

def send_file_content(conn, filename):
    with open(DIRECTORY + filename, 'r') as file:
        content = file.read()
    conn.send(json.dumps({'type': 'file_content', 'filename': filename, 'content': content}).encode('utf-8'))

def handle_edit_request(conn, filename):
    if filename not in files_in_edit:
        files_in_edit[filename] = clients[conn]
        send_file_content(conn, filename)
        notify_clients({'type': 'edit', 'filename': filename, 'editor': clients[conn]})
    else:
        conn.send(json.dumps({'type': 'error', 'message': 'File already in edit'}).encode('utf-8'))

def save_file_content(conn, filename, content):
    with open(DIRECTORY + filename, 'w') as file:
        file.write(content)
    notify_clients({'type': 'save', 'filename': filename, 'content': content})

def release_file(conn, filename):
    if files_in_edit.get(filename) == clients[conn]:
        del files_in_edit[filename]
        notify_clients({'type': 'release', 'filename': filename})

def add_file(filename):
    open(DIRECTORY + filename, 'w').close()
    notify_clients({'type': 'add', 'filename': filename})

def delete_file(filename):
    os.remove(DIRECTORY + filename)
    notify_clients({'type': 'delete', 'filename': filename})

def notify_clients(message):
    for conn in clients:
        conn.send(json.dumps(message).encode('utf-8'))

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server started at {HOST}:{PORT}')
        
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    start_server()
