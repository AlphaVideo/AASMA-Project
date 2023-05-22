"""
front = 0
back = 1
rotate left = 2
rotate right = 3
weapon = 4
"""

class GreedyPolicy:
    def __init__(self, env, agent_id: int = 0):
        self.env = env
        self.agent_id = agent_id
        self.agent = self.env.agents[self.agent_id]

        #!!!
        self.num_archers=1
        self.num_knights=1
        self.max_arrows = 10

    def __call__(self, observation, agent):

        #zombies info
        zombies_id = 1 + self.num_knights + 2*self.num_archers + self.max_arrows 
        zombies = observation[zombies_id:]

        #find closest zombie
        closest = zombies[0]
        for z in zombies:
            dist = z[0]
            if dist<closest[0] and dist!=0:
                closest = z
        
        #action based on type of agent -> ignorem
        #isKnight = True
        #if(self.agent_id < self.num_archers):
         #   isKnight = False

        #if (isKnight):
         #   action = 3
        #else:
         #   action = 2

        # set the default action
        action = self.default_action

        

        return action

    