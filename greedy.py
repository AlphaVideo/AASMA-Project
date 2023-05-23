"""
front = 0
back = 1
rotate left = 2
rotate right = 3
weapon = 4
"""

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

    def archerAction(self,position,closest):

        zombie_x = closest[1]
        zombie_y = closest[2]

        archer_x = position[3]
        archer_y = position[4]

        #print("zombie")
        #print([zombie_x,zombie_y])
        # if(archer_x == 0 and archer_y>0):
        #     print("DOWN")
        # if(archer_x == 0 and archer_y<0):
        #     print("UP")
        # if(archer_x > 0 and archer_y == 0):
        #     print("RIGHT")
        # if(archer_x < 0 and archer_y == 0):
        #     print("LEFT ")
        # if(archer_x<0 and archer_y <0):
        #     print("left up")
        # if(archer_x<0 and archer_y > 0):
        #     print("left down")
        # if(archer_x > 0 and archer_y < 0):
        #     print("right up")
        # if(archer_x > 0 and archer_y > 0):
        #     print("right down")
        
        print("\n")
        print("zombie_x - archer_x")
        print(zombie_x - archer_x)
        print("zombie_y - archer_y")
        print(zombie_y - archer_y)
        

        # if archer is facing zombie, then the vectors are symetric
        # used 0.4 because rotation not perfect, was a bit random
        if abs(zombie_x - archer_x) < 0.3 and abs(zombie_y - archer_y) < 0.3:
            print("ATTACK")
            # attack
            return 4
        
        #zombie a direita ACHO EU
        elif zombie_x > 0:
            #rotate right
            return 3
        
        #zombie a esquerda ACHO EU
        else:
            #rotate left
            return 2
        
        
        # if abs(closest[1]-position[3]) < 0.4 and abs(closest[2]-position[4]) < 0.4:
        #     return 4
        # elif(closest[2]>position[1]):
        #     return 3
        # else: return 2
    
    def knightAction(self,position, closest):
        #if inside radius, attack
        if closest[0] < 0.1 :
            return 4
        #get closer
        return 5

    def __call__(self, observation, agent):

        closest = self.closestZombie(observation)

        position = observation[0]

        if not closest.any():
            action = 5
        elif ("archer" in agent):
           action = self.archerAction(position,closest)
        else:
           action = self.knightAction(position,closest)
    

        return action

    