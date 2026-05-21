# Reserved for host client. Can play the game, and change the settings
import socket
import information.generic as generic
import pygame
import json
import time
from pygame_calls.game import gameLogic
from pygame_calls.enemy_classes import enemyClass
from pygame.math import Vector2

class Host:

    """
    A class to represent a host. 
    Client user that is able to manipulate the rules and setting of a session
    ...

    Attributes
    ----------
    position : list
        (x,y) position of a given player character
    velocity : float
        Controls the current speed of the player
    connection : object
        Handles the socket for connecting with the server

    """

    def __init__(self, position:list) -> None:
        self.connection = socket.socket()
        self.connection.connect((generic.SERVER_ADDRESS,generic.PORT))
        self.position = position
        self.velocity:float = 4

        data = self.connection.recv(generic.INT_SIZE)
        player_number = int.from_bytes(data, byteorder="big")
        if player_number == 1:
            self.controls = "wasd"
            self.color = (0, 255, 0)
            print("You are Player 1 (WASD)")
        else:
            self.controls = "arrows"
            self.color = (0, 0, 255)
            print("You are Player 2 (Arrows)")

        self.game_instruct = gameLogic.GameOperations()

        self.state = "move" # move state, attack state, dead state

    def setPosition(self, newPos):
        self.position = newPos

    def receive_str(self, connect, n_bytes: int) -> str:
        """
        :param n_bytes: The number of bytes to read from the current connection
        :return: The next string read from the current connection
        """
        data = connect.recv(n_bytes)
        return data.decode()

    def send_str(self,connect, value: str) -> None:
        connect.send(value.encode())

    def send_int(self, connect, value: int, n_bytes: int) -> None:
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))     

    def receive_int(self, connect, n_bytes: int) -> int:
        data = connect.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_object(self, connection, obj):
        """1º: envia tamanho, 2º: envia dados."""
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, generic.INT_SIZE)         # Envio do tamanho
        connection.send(data)              		# Envio do objeto

    def receive_object(self, connection):
        """1º: lê tamanho, 2º: lê dados."""
        size = self.receive_int(connection, generic.INT_SIZE)  	# Recebe o tamanho

        #print(f"DEBUG [Object Size Header]: {size} bytes") ##!! Debugging

        data = connection.recv(size)       			# Recebe o objeto
        return json.loads(data.decode('utf-8'))


    def execute(self):
        """
        Starts the client thread when called. Sets up the graphical interface for the user, allows handling of inputs, and draws the player and its partner as circles
        """
        clock = pygame.time.Clock()
        pygame.init()
        ##!! Need to declare screen size, in order to declare positions as % of screen size
        screen = pygame.display.set_mode((800, 600)) # width x height
        positions = {}

        internal_enemy_obj_list = [] # For enemy instance inside the host
        last_enemy_id = 0
        team_pos = self.position

        id = str(self.connection.getsockname())
        try:

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                old_position = self.position[:]
                self.position = self.game_instruct.movement(self.controls, self.position, self.velocity) # Updating position based on key input
                ##!! Reserved for a state of attack, and logic to define area of attack


                try: # Section for handling if current position should be sent
                    if old_position != self.position:
                        self.send_str(self.connection, generic.MOVE_OP)
                        self.send_object(self.connection, {"pos": self.position})
                        print(f"DEBUG: Current position at {self.position} has been sent")
                except (BrokenPipeError, ConnectionResetError):
                    return

                try: # Section for handling position broadcast
                    
                    opInstruct = self.receive_str(self.connection, generic.COMMAND_SIZE).strip()
                    if opInstruct == "pos":
                        positions = self.receive_object(self.connection)

                except BlockingIOError: #Operation could not be completed
                    pass

                screen.fill("black")
                playerPositions = positions.get("players", {})
                for addr_str, value in playerPositions.items():
                    if addr_str != id:
                        team_pos = value.get("pos", [0, 0])
                        pygame.draw.circle(screen, (255, 0, 0), (int(team_pos[0]), int(team_pos[1])), 10)
                
                ##!! Reserved for enemy positions
                enemyPositions = positions.get("enemies", {})

                for enem_id, info in enemyPositions.items(): # Define internal enemy objects
                    if any(obj.idEnemy == int(enem_id) for obj in internal_enemy_obj_list): ##! If already present in list, skip
                        continue
                    else:

                        internal_enemy_obj_list.append(enemyClass.Enemy(int(enem_id), [info[0][0], info[0][1]], info[1])) # [id, position, type]
                        last_enemy_id = int(enem_id) #! Might break in not in order, change to check actual existence

                ##!! Add logic for creating enemy object here. Use that list to define the sizing of circles. Update their positiojn acoording to velocity
                ##!! Need to define section here (maybe class method) to determine the orientation of their velocity

                for enemy_instance in internal_enemy_obj_list: ##!! Need to also check for colission with other enemies
                    if not enemy_instance.tag_colission(self.position, 10, enemy_instance.get_position(), enemy_instance.get_size()) and\
                       not enemy_instance.tag_colission(team_pos, 10, enemy_instance.get_position(), enemy_instance.get_size()):
                        
                        # [current_pos] + [position shift towards a given direction based on quadrant]
                        enemy_instance.set_position(Vector2(enemy_instance.get_position()) + Vector2(enemy_instance.get_quadrant_mult()) * enemy_instance.get_velocity())
                        
                        ##!! There must be a way to also check if its hitting the circle for the other player without sending actual information
                        pygame.draw.circle(screen, (225, 225, 125), (enemy_instance.get_position()[0], enemy_instance.get_position()[1]), enemy_instance.get_size())

                    elif True: ##!! If it is affected by a hit....declared as points, eliminated
                        pass

                    elif True: ##!! On colission, bounce or do damage (or both)
                        pass

                pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), 10)
                
                ##!! Since movement has finalized, you can now check for colission, since both entities for enemies and players are at the final position, and you can check
                ##!! if they bumped into each other or not



                pygame.display.flip()
                clock.tick(60)

        except Exception as e:
            print("Error " + str(e))
        finally:
            pygame.quit()
