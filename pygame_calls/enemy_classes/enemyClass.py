class Enemy:
    """
    
    Enemy class, handles the related atributes


    ...

    ...

    ...


    self.quadrant_mult:
        Handles the way velocity will be handled. An enemy spawned in the second quadrant will move towards the 4th, one in 1st quadrant will move towards the 2nd, and vice versa
    """

    def __init__(self, idEnemy: str, position: list, type: int) -> None:

        self.idEnemy = idEnemy
        self.position = position
        self.velocity:float = 1
        self.type = type ##!! Need to be swapped for a probability from 1 to 100, to determine type
        self.size = 5
        ##!! Need to have a seed associated with slight randomness, to generate variation in direction
        if position[0] <= 400: # If it spawns on a quadrant, it must move towards the opposite quadrant
            if position[1] >= 300: # 2nd quadrant or 3rd
                self.quadrant_mult = [1, -1] # Positive x velocity, negative y velocity
            else:
                self.quadrant_mult = [1, 1]
        else:
            if position[1] >=300: # 1st quadrant or 4th
                self.quadrant_mult = [-1, -1]
            else:
                self.quadrant_mult = [-1, 1]

    def tag_colission(self, player_pos, player_radius, enemy_pos, enemy_radius):
        """
        Obter vetor, comparar distancia através do raio depois de calcular a hipotenusa, devolver verdadeiro se ocorrer colisão (falso se não ocorrer)
        """
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        sq_distance = dx**2 + dy**2
        sq_radii_sum = (player_radius + enemy_radius)**2
        return sq_distance < sq_radii_sum
    

    def bounce(self): ## Bounce into a given direction after colission
        pass

    def move(self): ##!! Reserved for handling special enemy movement
        pass

    def despawn(self): ##!! Reserved for despawning upon exiting game borders
        pass



    def get_position(self):
        return self.position
    
    def set_position(self,new_pos):
        self.position = new_pos

    def get_size(self):
        return self.size
    
    def get_quadrant_mult(self):
        return self.quadrant_mult

    def get_velocity(self):
        return self.velocity

