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
        #zombies info
        zombies_id = 1 + self.num_knights + 2*self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        #find closest zombie
        closest = zombies[0]
        for z in zombies:
            dist = z[0]
            if dist<closest[0] and dist!=0:
                closest = z
        return closest
    
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
        if closest[0] < 0.05:
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
        closest = self.closestZombie(observation)

        # [ 0  x  y  rotX  rotY ]
        position = observation[0]

        if not closest.any():
            action = 5
        elif ("archer" in agent):
           action = self.archerAction(position,closest)
        elif ("knight" in agent):
           action = self.knightAction(position,closest)
    

        return action

    