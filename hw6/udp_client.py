#!/usr/bin/env python3
import socket

# UDP 클라이언트 소켓 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)  # 서버의 IP와 포트 

print("UDP 클라이언트 실행. 명령 입력 (send, receive, quit)")

while True:
    # 사용자로부터 명령 입력 받기
    command = input("명령을 입력하세요: ").strip()
    if not command:
        continue

    # 서버로 명령 전송
    client_socket.sendto(command.encode(), server_address)
    
    # 'quit' 입력 시 클라이언트 종료
    if command.lower() == "quit":
        print("프로그램 종료.")
        break

    # 서버로부터 응답 수신
    data, _ = client_socket.recvfrom(4096)
    response = data.decode()
    print("서버 응답:", response)

client_socket.close()
