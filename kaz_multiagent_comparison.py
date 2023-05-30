import os
import json
import pygame
import argparse
import numpy as np
from typing import Sequence

import knights_archers_zombies
import greedy
from src import constants as const

N_CASES=2
N_EPISODES=3
OUTPUT_FILES=["CASE1.txt", "CASE2.txt"]

def run_multi_agent(environment, agents: Sequence, n_episodes: int) -> np.ndarray:

    results = np.zeros(n_episodes)

#     for episode in range(n_episodes):

#         steps = 0
#         terminals = [False for _ in range(len(agents))]
#         observations = environment.reset()

#         while not all(terminals):
#             steps += 1
#             # TODO - Main Loop (4-6 lines of code)
#             for observations, agent in zip(observations, agents):
#                 agent.see(observations)
#             actions = [agent.action() for agent in agents]
#             next_observations, rewards, terminals, info = environment.step(actions)
#             observations = next_observations
#         results[episode] = steps

#         environment.close()

    return results

# Delete result files from previous executions
for name in OUTPUT_FILES:
    os.remove(name)

# Create an environment for each test case
# This is so their output goes to different files
envs = []
for i in range(N_CASES):
    env = knights_archers_zombies.env(
    spawn_rate=const.SPAWN_RATE,
    num_archers=const.NUM_ARCHERS,
    num_knights=const.NUM_KNIGHTS,
    max_zombies=const.MAX_ZOMBIES, 
    max_arrows=const.MAX_ARROWS,
    max_cycles=const.MAX_CYCLES,
    vector_state=True,
    terminal_results=False,
    output_file=OUTPUT_FILES[i]
    )
    envs += [env]

clock = pygame.time.Clock()

for env in envs:
    for i in  range(N_EPISODES):
        # Reset environment for new episode
        env.reset()
        for agent in env.agent_iter():
            clock.tick(env.metadata["render_fps"])

            observation, reward, termination, truncation, info = env.last()
            
            greedyPolicy = greedy.GreedyPolicy(env)

            #action = env.action_space(agent).sample()
            action = greedyPolicy(observation,agent) #!!! -> esta linha + ficheiro greedy

            if termination or truncation:
                env.step(None)
            else:
                env.step(action)

# f = open("results.txt", 'r')

# for line in f.readlines():
#     result = json.loads(line)
#     print(result)