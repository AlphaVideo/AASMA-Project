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
    def __init__(self, env, strategy=const.STRATEGY):
        self.env = env
        self.strategy = strategy

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

        if(closest.any()):
            return closest
        else:
            return None
    
    def zombieNearBottom(self, observation): 
        zombies_id = 1 + 2*self.num_knights + self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        """
        Positions are relative: 
        The closer the zombie to archer => the higher the value of y 
        Zombies before archer on y axis will have value < 0
        Zombies past archer on y axis will have value > 0 
        """

        closestToBottom = zombies[0] #First zombie
        max_y = zombies[0][2] #Y of first zombie

        for z in zombies:
            #z[4] => angle of entity with the "world"
            #This value is 1 when the entity is alive, 0 when dead/not in use
            if z[4] == 1 and z[2] > max_y:
                max_y = z[2]
                closestToBottom = z
        
        if(closestToBottom.any()):
            return closestToBottom  
        else:
            return None
    
    def unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)
    
    def vectors_near_collinear(self, v1, v2):
        #True if vectors are within a margin
        return abs(v1[0] - v2[0]) <= const.ANGLE_MARGIN and abs(v1[1] - v2[1]) <= const.ANGLE_MARGIN
    
    def move_agent_to_right(self, v1, v2):
        return abs(v1[1] - v2[0]) <= const.ARCHER_POSTION_RADIUS and abs(v1[2] - v2[1]) <= const.ARCHER_POSTION_RADIUS

    def archerAction(self, position, target, agent_id):

        archer_direction_v = self.unit_vector(np.array([position[3], position[4]]))
        zombie_relational_v = self.unit_vector(np.array([target[1], target[2]]))
        right_vector = self.unit_vector(np.array([1, 0]))
        right_position_goal = [0.7, 0.825]
        #Archer can have better accuracy if he aims for a zombie position slightly lower than current position:
        #Lower y on game screen => > y_value
        projected_zombie_v = self.unit_vector(np.array([zombie_relational_v[0], zombie_relational_v[1]+const.ARCHER_TARGET_OFFSET]))
        
        ## Position 2nd archer to the right
        if int(agent_id) == 1:
            if not self.move_agent_to_right(position, right_position_goal):
                if not self.vectors_near_collinear(archer_direction_v, right_vector):
                    return 3
                else:
                    return 0
                
        #The nearer the zombie is to the archer, the safer it is to use non-projected direction
        chosen_vector = None
        if target[2] >= const.ARCHER_TARGET_CLOSE:
            # Case where zombie is close => original direction
            chosen_vector = zombie_relational_v
        else:
            # Case where zombie is far => projected direction
            chosen_vector = projected_zombie_v

        #Closest rotation is given by the sign of the determinant of the matrix given by the vectors [u, v]
        vector_mat_det = archer_direction_v[0]*chosen_vector[1] - archer_direction_v[1]*chosen_vector[0]
        
        # If Archer is facing Zombie, then the vectors are colinear
        if(self.vectors_near_collinear(archer_direction_v, chosen_vector)):
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
    
    def knightAction(self, position, target, orderedZombies):


        knight_direction_v = self.unit_vector(np.array([position[3], position[4]]))
        zombie_relational_v = self.unit_vector(np.array([target[1], target[2]]))

        vector_mat_det = knight_direction_v[0]*zombie_relational_v[1] - knight_direction_v[1]*zombie_relational_v[0]

        for zombie in orderedZombies:
            if zombie[0] < const.KNIGHT_ATTACK_RADIUS:
                return 4

        #if inside radius, attack
        if target[0] < const.KNIGHT_ATTACK_RADIUS:
            return 4
        elif (self.vectors_near_collinear(knight_direction_v, zombie_relational_v)):
            #get closer
            return 0
        #Pos. Determinant => closest rotation to collinear is clockwise
        elif vector_mat_det > 0:
            #rotate right
            return 3
        #Neg. Determinant => closest rotation to collinear is anti-clockwise
        else:
            #rotate left
            return 2

    def agentPriority(self, observation, agent):
        # priority: archer 1 > ... > archer n > knight 1 > ... > knight m

        #test = -1

        agent_id = int(agent[7:])
        if "archer" in agent: agent_id += self.num_knights

        #list agents
        knight_endIndex = 1 + self.num_archers + self.num_knights
        archer_endIndex = 1 + self.num_archers
        agents = list(observation[archer_endIndex:knight_endIndex]) + list(observation[1:archer_endIndex])
        #agents_endIndex = 1 + self.num_archers + self.num_knights
        #agents = observation[1:agents_endIndex]

        priority = agent_id
        
        #check if there are dead agents and ajust priorities
        for i in range(len(agents)): 
            if i >= agent_id: 
                #if(test==1): print("break: i= ",i)
                break
            elif not agents[i].any():
                priority -= 1
                #test = 1
                #print("i:",i," agent_id: ", agent_id, "new_priority: ", priority)
                

        #if test == 1: print(agents,"\n-------------------------------")

        return priority

    def orderFunc(self,z):
        return z[2]

    def orderZombies(self, observation):
        #Zombie lines are found after current_agent + archers + knights + swords + arrows
        zombies_id = 1 + 2*self.num_knights + self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        # filter dead zombies
        zombies = list(filter(lambda z: z.any(), zombies))

        # sort them by relative y !!
        #zombies.sort(key=self.orderFunc)

        # sort them by absolute y (!! i think)
        agent_pos = observation[0]
        zombies.sort(key=lambda z: agent_pos[2] - z[2])

        return zombies

    def socialConventions(self,observation,agent):

        priority = self.agentPriority(observation,agent)
        orderedZombies = self.orderZombies(observation)

        if priority < len(orderedZombies):
            return orderedZombies[priority]
        elif len(orderedZombies)>0:
            return orderedZombies[-1]
        else:
            return None

    def closestTo(self,zombie,agents,agent_pos):
        # posicao absoluta do zombie
        abs_zombie = [agent_pos[1]-zombie[1],agent_pos[2]-zombie[2]]

        # base : proprio agente
        closest = 0
        min_dist = math.dist(abs_zombie,[agent_pos[1]-agents[0][1],agent_pos[2]-agents[0][2]])

        for i in range(len(agents)):
            abs_agent = [agent_pos[1]-agents[i][1],agent_pos[2]-agents[i][2]]
            dist = math.dist(abs_zombie,abs_agent)
            if dist <= min_dist:
                closest = i
                min_dist = dist
        
        return closest

    def roles(self,observation):
        # 1.olhar para os 4 zombies mais proximos
        # 2. ver a distancia de cada agente a cada zombie
        # 3. atribuir role ao mais proximo

        orderedZombies = self.orderZombies(observation)
        agent_pos = observation[0]
        agents_endIndex = 1 + self.num_archers + self.num_knights
        agents = observation[1:agents_endIndex]

        for z in orderedZombies:

            closestAgent = self.closestTo(z,agents,agent_pos)

            if agents[closestAgent][0] == 0: #is itself
                return z
            else:
                agents = np.delete(agents,closestAgent,axis=0)

        return None

    def __call__(self, observation, agent):

        # observations: [ AbsDist  RelX  RelY  rotX  rotY ]

        # position: [ 0  x  y  rotX  rotY ]
        position = observation[0]

        agent_id = agent[7:]

        #greedy
        if self.strategy == 0 and "archer" in agent:
            target = self.zombieNearBottom(observation)
        if self.strategy == 0 and "knight" in agent:
            target = self.closestZombie(observation)
        #socia conventions
        elif self.strategy == 1:  
            target = self.socialConventions(observation,agent)
        #roles
        else:
            target = self.roles(observation)

        #check if there's a target
        if target is None: return 5

        #get action
        if ("archer" in agent):
            action = self.archerAction(position, target,agent_id)

        elif ("knight" in agent):
            orderedZombies = self.orderZombies(observation)
            action = self.knightAction(position, target, orderedZombies)

        return action

    