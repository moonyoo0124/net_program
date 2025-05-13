import socket
import threading
import time

HOST = 'localhost'
PORT = 5555
BUFSIZE = 1024

# 클라이언트 소켓과 주소, ID를 저장하는 리스트 
clients = []
clients_lock = threading.Lock() # 리스트 동기화

def broadcast(message, sender_socket=None):
    """모든 클라이언트에게 메시지를 전송 (선택적으로 발신자 제외)"""
    with clients_lock:
        for client_socket, client_address, client_id in clients:
            if sender_socket is None or client_socket != sender_socket: # 발신자를 지정하면 해당 발신자 제외
                try:
                    client_socket.send(message.encode())
                except socket.error:
                    print(f"Error sending to {client_address}")
                    pass 

def handle_client(conn, addr):
    """개별 클라이언트를 처리하는 스레드 함수"""
    client_id = ""
    try:
        # 첫 번째 메시지는 클라이언트 ID로 간주
        client_id_data = conn.recv(BUFSIZE)
        if not client_id_data:
            print(f"Client {addr} disconnected before sending ID.")
            return
        client_id = client_id_data.decode().strip()
        
        with clients_lock:
            clients.append((conn, addr, client_id))
        
        print(f"[{time.asctime()}] New client connected: {addr}, ID: {client_id}")
        broadcast(f"[{time.asctime()}] *** {client_id} has joined the chat. ***", conn) # 접속 알림 (본인 제외)

        while True:
            data = conn.recv(BUFSIZE)
            if not data or data.decode().strip().lower() == 'quit':
                break
            
            message_to_send = f"[{time.asctime()}] {client_id}: {data.decode().strip()}"
            print(message_to_send) # 서버 콘솔에도 메시지 출력
            broadcast(message_to_send, conn) # 자신을 제외한 모든 클라이언트에게 메시지 전송

    except socket.error as e:
        print(f"Socket error with client {addr} (ID: {client_id}): {e}")
    except Exception as e:
        print(f"Error with client {addr} (ID: {client_id}): {e}")
    finally:
        with clients_lock:
            # clients 리스트에서 해당 클라이언트 정보 찾아서 제거
            client_to_remove = None
            for client_info in clients:
                if client_info[0] == conn:
                    client_to_remove = client_info
                    break
            if client_to_remove:
                clients.remove(client_to_remove)
                # client_id가 할당된 경우에만 퇴장 메시지 전송
                if client_id:
                    print(f"[{time.asctime()}] Client disconnected: {addr}, ID: {client_id}")
                    broadcast(f"[{time.asctime()}] *** {client_id} has left the chat. ***")
            else:
                 print(f"[{time.asctime()}] Client {addr} (ID unknown or already removed) disconnected.")

        conn.close()

def start_server():
    """서버 시작 함수"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5) # 최대 5개 동시 연결 대기 
        print(f"Chat server started on {HOST}:{PORT}")
        print("Waiting for clients...")

        while True:
            conn, addr = server_socket.accept() # 클라이언트 연결 수락 
            # 각 클라이언트에 대해 새 스레드 생성하여 handle_client 함수 실행 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True # 메인 스레드 종료 시 서브 스레드도 종료되도록 설정 
            thread.start()
            
    except socket.error as e:
        print(f"Server socket error: {e}")
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        if 'server_socket' in locals():
            server_socket.close()
        print("Server stopped.")

if __name__ == '__main__':
    start_server()