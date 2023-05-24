"""
front = 0
back = 1
rotate left = 2
rotate right = 3
weapon = 4
"""

import numpy as np

class GreedyPolicy:
    def __init__(self, env):
        self.env = env
        #self.agent_id = agent_id
        #self.agent = self.env.agents[self.agent_id]

        #!!!
        self.num_archers=1
        self.num_knights=1
        self.max_arrows = 10

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
        return abs(v1[0] - v2[0]) < 0.1 and abs(v1[1] - v2[1]) < 0.1

    def archerAction(self,position,closest):

        archer_direction_v = self.unit_vector(np.array([position[3], position[4]]))
        zombie_relational_v = self.unit_vector(np.array([closest[1], closest[2]]))
        
        
        # if archer is facing zombie, then the vectors are colinear
        # go by angle since relational vector (closest) isn't normalized
        if(self.is_close(archer_direction_v,zombie_relational_v)):
            # attack
            return 4
        
        #zombie a direita ACHO EU
        elif zombie_relational_v[0] > archer_direction_v[0]:
            #rotate right
            return 3
        
        #zombie a esquerda ACHO EU
        else:
            #rotate left
            return 2
        
    
    def knightAction(self,position, closest):
        #if inside radius, attack
        if closest[0] < 0.1 :
            return 4
        #get closer
        return 5

    def __call__(self, observation, agent):

        # [ AbsDist  RelX  RelY  rotX  rotY ]
        closest = self.closestZombie(observation)

        # [ 0  x  y  rotX  rotY ]
        position = observation[0]

        if not closest.any():
            action = 5
        elif ("archer" in agent):
           action = self.archerAction(position,closest)
        else:
           action = self.knightAction(position,closest)
    

        return action

    