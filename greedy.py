"""
front = 0
back = 1
rotate left = 2
rotate right = 3
weapon = 4
"""

import numpy as np
import math

from src import constants as const

class GreedyPolicy:
    def __init__(self, env):
        self.env = env
        #self.agent_id = agent_id
        #self.agent = self.env.agents[self.agent_id]

        #!!!
        self.num_archers=const.NUM_ARCHERS
        self.num_knights=const.NUM_KNIGHTS
        self.max_arrows =const.MAX_ARROWS

    def closestZombie(self,observation):
        #Zombie lines are found after current_agent + archers + knights + swords + arrows
        zombies_id = 1 + 2*self.num_knights + self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        #find closest zombie
        closest = zombies[0]
        for z in zombies:
            dist = z[0]
            if dist<closest[0] and dist!=0:
                closest = z
        return closest
    
    def zombieNearBottom(self, observation):
        zombies_id = 1 + 2*self.num_knights + self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        """
        Positions are relative: 
        Closest zombie to archer => higher value of y 
        Zombies before archer on y axis will have value < 0
        Zombies past archer on y axis will have value > 0 
        """

        closestToBottom = zombies[0] #First zombie
        max_y = zombies[0][2] #Y of first zombie

        for z in zombies:
            #z[4] => angle of entity with the "world"
            #This value is 1 when the entity is alive, 0 when dead/not in use
            if z[4] == 1:
                if z[2] > max_y:
                    max_y = z[2]
                    closestToBottom = z
            
        return closestToBottom
    
    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)
    
    def is_close(self, v1, v2):
        #Attempt to hit target by a margin
        return abs(v1[0] - v2[0]) <= const.ANGLE_MARGIN and abs(v1[1] - v2[1]) <= const.ANGLE_MARGIN

    def archerAction(self,position,closest):

        archer_direction_v = self.unit_vector(np.array([position[3], position[4]]))
        zombie_relational_v = self.unit_vector(np.array([closest[1], closest[2]]))

        #Closest rotation is given by the sign of the determinant of the matrix given by the vectors [u, v]
        vector_mat_det = archer_direction_v[0]*zombie_relational_v[1] - archer_direction_v[1]*zombie_relational_v[0]
        
        # If Archer is facing Zombie, then the vectors are colinear
        if(self.is_close(archer_direction_v,zombie_relational_v)):
            # attack
            return 4
        
        #Pos. Determinant => closest rotation to colinear is clockwise
        elif vector_mat_det > 0:
            #rotate right
            return 3
        
        #Neg. Determinant => closest rotation to colinear is anti-clockwise
        else:
            #rotate left
            return 2
        
    
    def knightAction(self, position, closest):


        knight_direction_v = self.unit_vector(np.array([position[3], position[4]]))
        zombie_relational_v = self.unit_vector(np.array([closest[1], closest[2]]))

        vector_mat_det = knight_direction_v[0]*zombie_relational_v[1] - knight_direction_v[1]*zombie_relational_v[0]

        #if inside radius, attack
        if closest[0] < const.KNIGHT_ATTACK_RADIUS:
            return 4
        elif (self.is_close(knight_direction_v, zombie_relational_v)):
            #get closer
            return 0
        #Pos. Determinant => closest rotation to colinear is clockwise
        elif vector_mat_det > 0:
            #rotate right
            return 3
        #Neg. Determinant => closest rotation to colinear is anti-clockwise
        else:
            #rotate left
            return 2


    def __call__(self, observation, agent):

        # [ AbsDist  RelX  RelY  rotX  rotY ]

        # [ 0  x  y  rotX  rotY ]
        position = observation[0]

        if ("archer" in agent):
            # [ AbsDist  RelX  RelY  rotX  rotY ]
            target = self.zombieNearBottom(observation)
            if not target.any():
                action = 5
            else:
                action = self.archerAction(position,target)

        elif ("knight" in agent):
            # [ AbsDist  RelX  RelY  rotX  rotY ]
            closest = self.closestZombie(observation)
            if not closest.any():
                action = 5
            else:
                action = self.knightAction(position,closest)
    
        return action

    