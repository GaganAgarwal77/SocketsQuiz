import socket
import sys
import time
import select
import random
from Questions_Answers import Questions, Answers


clients_list = []
client_address_list = []

Points = []

max_players = 3

for i in range(max_players):
    Points.append(0)


def Connecting_Clients():  # Connecting to clients until max_players have connected
    player_no = 1
    while True:
        client, address = server_socket.accept()
        server_socket.setblocking(1)  # To avoid Timeout of the server
        clients_list.append(client)
        client_address_list.append(address)
        if player_no <= max_players:
            print(
                f"Connected to Client {player_no} at address: {address[0]} and port: {address[1]}")
            client.send(("\n--------------------------Welcome to this Amazing Quiz!-----------------------\n\nThe rules are simple:\n1. There will be many questions each with 4 options.\n2.You have to press any key to hit the buzzer within 10 seconds, if no one presses the buzzer the game moves on.\n3. The first one to hit the buzzer gets the chance to answer the question within 10 seconds.\n4. You get 1 Point for every Correct Answer and -0.5 Points for wrong answer or if the time runs out.\n The First One to Reach 5 points wins the Quiz!\n\t\t\t\tGOOD LUCK!").encode('utf-8'))
            time.sleep(1)
            client.send((f"You are Player: {player_no}\n").encode('utf-8'))
            if player_no == max_players:
                print(f"All {max_players} Clients connected")
                break
            player_no += 1


def display_points(Points):  # To display the points on the server terminal
    print("Current Points: ")
    for i in range(max_players):
        print(f"Player {i+1}: {Points[i]}")


def Start_Quiz():  # Start the quiz and ask questions  at random from the Questions array and determine points
    for i in range(len(Questions)):
        question_index = random.randint(0, 1000) % len(Questions)
        for client in clients_list:
            client.send((
                f'Q{i+1})' + Questions[question_index] + '\n').encode('utf-8'))

        response = select.select(clients_list, [], [], 10)
        if(len(response[0]) > 0):
            client_name = response[0][0]
            response_to_buzzer = client_name.recv(1024)
            response_to_buzzer = response_to_buzzer.decode("utf-8")
            for client in clients_list:
                if client != client_name:
                    client.send((
                        f"Sorry, Player {clients_list.index(client_name)+1} has pressed the buzzer.\n").encode('utf-8'))
            for client in clients_list:
                if client == client_name:
                    client_index = clients_list.index(client)

            if len(response_to_buzzer) > 0 or response_to_buzzer == None:
                client_name.send((
                    "Good Job! You pressed the buzzer first, now answer the question within 10 secs").encode('utf-8'))
                response_to_answer = select.select([client_name], [], [], 10)
                if len(response_to_answer[0]) > 0:
                    answer = client_name.recv(1024).decode("utf-8")
                    if answer == Answers[question_index]:
                        Points[client_index] += 1
                        client_name.send((
                            "Correct Answer! You get 1 Point\n").encode('utf-8'))
                        if Points[client_index] >= 5:
                            break
                    else:
                        client_name.send((
                            "Wrong Answer! You get -0.5 Points\n").encode('utf-8'))
                        Points[client_index] -= 0.5
                        time.sleep(1)
                else:
                    client_name.send((
                        "You didn't answer within 10 seconds, You get -0.5 Points\n").encode('utf-8'))
                    Points[client_index] -= 0.5
                    time.sleep(1)

        else:
            for client in clients_list:
                client.send((
                    "Nobody pressed the buzzer. So Moving on to the next question\n").encode('utf-8'))
        display_points(Points)
        Questions.pop(question_index)
        Answers.pop(question_index)


def End_Quiz():    # Reveal final standings and declare the winner
    maximum = 0
    player_id = 0
    for i in range(len(clients_list)):
        if Points[i] > maximum:
            player_id = i
            maximum = Points[i]

    display_points(Points)

    for client in clients_list:
        client.send(("END QUIZ").encode('utf-8'))
        time.sleep(0.1)
        msg = "Final Standings: \n"
        for i in range(max_players):
            msg += f"Player {i+1}: {Points[i]}\n"
        client.send(msg.encode('utf-8'))

        Tie = False
        same = Points[0]
        for points in Points:
            if points == same:
                tie = True

        if Tie is True:
            client.send((
                f"Its a tie between the {max_players} players , each with {maximum} Points").encode('utf-8'))

        if clients_list.index(client) != player_id:
            client.send((
                f"The winner is Player: {player_id+1} with {maximum} Points\n\nThank You For Playing!").encode('utf-8'))
        else:
            client.send((
                f"\nCongratulations! You are the winner with {maximum} Points\n").encode('utf-8'))


host = "127.0.0.1"
port = input("Enter the Port No. : ")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((host, int(port)))
server_socket.listen(5)
print("Server Connection Established, Kindly start connecting the clients.")
Connecting_Clients()
Start_Quiz()
End_Quiz()
