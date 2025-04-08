#!/usr/bin/env python3
import socket

# UDP 서버 소켓 생성 및 바인딩
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', 12345)  # ''는 모든 인터페이스, 포트 12345 사용
server_socket.bind(server_address)

# 메일박스를 저장할 딕셔너리: 키는 mboxID, 값은 메시지 리스트(큐)
mailboxes = {}

print("UDP 서버 실행 중... 포트:", server_address[1])

while True:
    # 클라이언트로부터 데이터를 수신 (최대 4096 바이트)
    data, client_addr = server_socket.recvfrom(4096)
    msg = data.decode().strip()  # 받은 데이터를 문자열로 디코딩 후 양쪽 공백 제거
    print(f"클라이언트({client_addr})로부터 받은 메시지: {msg}")

    # "quit" 메시지를 수신하면 서버 종료
    if msg.lower() == "quit":
        print("quit 메시지 수신. 서버 종료.")
        break

    tokens = msg.split()
    if not tokens:
        continue

    command = tokens[0].lower()
    response = ""

    if command == "send":
        # 형식: send [mboxID] message
        if len(tokens) < 3:
            response = "Invalid send command"
        else:
            mboxID = tokens[1]
            # mboxID 이후의 모든 토큰을 하나의 문자열로 message로 취급
            message = " ".join(tokens[2:])
            if mboxID not in mailboxes:
                mailboxes[mboxID] = []
            mailboxes[mboxID].append(message)
            response = "OK"
    elif command == "receive":
        # 형식: receive [mboxID]
        if len(tokens) != 2:
            response = "Invalid receive command"
        else:
            mboxID = tokens[1]
            if mboxID in mailboxes and mailboxes[mboxID]:
                # 가장 먼저 저장된 메시지 꺼내기 (FIFO)
                response = mailboxes[mboxID].pop(0)
            else:
                response = "No messages"
    else:
        response = "Unknown command"

    # 응답 메시지 서버 -> 클라이언트 전송
    server_socket.sendto(response.encode(), client_addr)
    print(f"클라이언트({client_addr})에게 전송한 응답: {response}")

server_socket.close()
