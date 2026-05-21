##!! Reserved for logic as to where to call the enemy spawning. should be called on server side. Graphical element shouls be presented
## in client side


from server import gameState
import threading
import random
import time

def enemyCreationThread(game_state): ##!! Clean and refactor in order to handle nested dictionaries (positions from players != positions from enemies)
    """
    Starts the thread for enemy creation thread thread, in order to define enemy position and update the dict in gameState
    """
    print("Initializing server thread")
    spawn_thread = threading.Thread(target=enemySpawning, args=(game_state,), daemon=True)
    spawn_thread.start()
    return spawn_thread

def enemySpawning(game_state):##!! Need to add an enemy logic generation here, based on the display size obtained
    ##!! As it stands now, they will only show up from the corner sections due to the way ranges are set up
    valid_positions_x_ranges = [[-100, -20], [820, 900]] # left to -20, or right to 820
    valid_positions_y_ranges = [[620, 700],[-100, -20]]
    enemy_id = 1 ##!! this will reset, need to fix
    enemy_type = random.randint(1,100)
    while enemy_id < 550:
        ## The enemy spawn is called and declared to the player, but only the game client actually defines what the enemy will be
        relative_position = [random.choice(valid_positions_x_ranges), random.choice(valid_positions_y_ranges)]
        enemy_position = [random.randint(relative_position[0][0], relative_position[0][1]),
                          random.randint(relative_position[1][0], relative_position[1][1])]
        
        print("Enemy added at position " + str(enemy_position))
        if game_state.get_enemy_count() < 30: ##!! to be replaced with parameter that is presented through menu, make a function so it spawns fasters the less enemies there are
            game_state.add_enemy({enemy_id: [enemy_position,enemy_type]})
            enemy_id += 1
        time.sleep(2) ##!! to be replaced with a parameter for rate of spawning
         # screen = pygame.display.set_mode((800, 600)) , need something similar to this without pygame, to define size