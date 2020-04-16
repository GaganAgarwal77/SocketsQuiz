import socket
import time
import select
import sys
from termios import tcflush, TCIFLUSH

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = input("Enter Port No. : ")
client_socket.connect((host, int(port)))

MAX = 1024  # Max message length

welcome_message = (client_socket.recv(MAX)).decode("utf-8")
print(welcome_message)

player_id_message = (client_socket.recv(MAX)).decode("utf-8")
print(player_id_message)

while True:
    question_data = (client_socket.recv(MAX)).decode("utf-8")
    if question_data == "END QUIZ":  # On receiving this from the server the client side stops running
        break
    print(question_data)

    tcflush(sys.stdin, TCIFLUSH)
    buzzer_response = select.select([sys.stdin, client_socket], [], [], 10)
    if len(buzzer_response[0]) > 0:
        if buzzer_response[0][0] == sys.stdin:
            key_input = input()
            client_socket.send(key_input.encode('utf-8'))

    data = (client_socket.recv(MAX)).decode("utf-8")
    print(data)
    if data == 'Good Job! You pressed the buzzer first, now answer the question within 10 secs':
        tcflush(sys.stdin, TCIFLUSH)
        question_response = select.select(
            [sys.stdin, client_socket], [], [], 10)
        if len(question_response[0]) > 0:
            if question_response[0][0] == sys.stdin:
                answer = input('> ')
                client_socket.send(answer.encode('utf-8'))
            reply = (client_socket.recv(MAX)).decode("utf-8")
            print(reply)

standings = (client_socket.recv(MAX)).decode("utf-8")
print(standings)
result = (client_socket.recv(MAX)).decode("utf-8")
print(result)
