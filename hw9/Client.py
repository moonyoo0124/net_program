import socket
import threading
import sys

HOST = 'localhost'
PORT = 5555
BUFSIZE = 1024

def receive_messages(sock):
    """서버로부터 메시지를 수신하여 출력하는 함수 (스레드에서 실행)"""
    while True:
        try:
            data = sock.recv(BUFSIZE)
            if not data:
                print("\nDisconnected from the server.")
                break
            print(data.decode())
        except socket.error:
            print("\nError receiving message or server closed connection.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break
    sock.close()
    print("Receive thread finished.")
    # 프로그램 강제 종료 또는 사용자에게 알림 후 종료 유도
    # 여기서는 단순화하여 스레드만 종료
    # os._exit(0) # 필요한 경우 프로그램 즉시 종료

def start_client():
    """클라이언트 시작 함수"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT)) # 서버에 연결 
    except socket.error as e:
        print(f"Failed to connect to server {HOST}:{PORT}. Error: {e}")
        return

    # 사용자 ID 입력 및 서버로 전송
    my_id = input("Enter your ID: ")
    client_socket.send(my_id.encode()) # ID를 서버로 전송 (UDP 예제 참고)

    # 메시지 수신을 위한 스레드 시작
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.daemon = True # 메인 스레드 종료 시 서브 스레드도 종료 (UDP 예제 참고)
    recv_thread.start()

    print(f"\nConnected to chat server as '{my_id}'. Type 'quit' to exit.")
    
    try:
        while True:
            message = input() # 사용자로부터 메시지 입력 
            if message.strip().lower() == 'quit':
                client_socket.send('quit'.encode()) # 'quit' 메시지를 서버로 전송
                break # 입력 루프 종료
            
            # 실제 메시지 전송 시 ID는 서버에서 붙여주므로 여기서는 메시지만 전송
            client_socket.send(message.encode()) # 메시지를 서버로 전송 
            
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client_socket.send('quit'.encode()) # Ctrl+C 입력 시 'quit' 전송 시도
    except socket.error as e:
        print(f"Socket error during sending: {e}")
    except Exception as e:
        print(f"An error occurred during input/send: {e}")
    finally:
        print("Closing your connection...")
        client_socket.close() # 소켓 닫기
        # recv_thread.join() # 수신 스레드가 완전히 종료될 때까지 대기 (선택 사항)
        print("Disconnected.")

if __name__ == '__main__':
    start_client()