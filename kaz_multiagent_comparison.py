import os
import json
import pygame
import argparse
import numpy as np
from typing import Sequence

import graph_utils
import knights_archers_zombies
import greedy
from src import constants as const

N_CASES=len(const.STRATEGY_LIST)
N_EPISODES=3
OUTPUT_FILES=[const.STRATEGY_LIST[0]+".txt", const.STRATEGY_LIST[1]+".txt", const.STRATEGY_LIST[2]+".txt"]
COLORS=["green", "blue", "purple"]

# Delete result files from previous executions
for name in OUTPUT_FILES:
    if os.path.exists(name):
        os.remove(name)

# Create an environment for each test case
# This is so their output goes to different files
envs = []
for i in range(N_CASES):
    env = knights_archers_zombies.env(render_mode="human",
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

strategy_index = 0
for env in envs: 
    for i in range(N_EPISODES):
        # Reset environment for new episode
        env.reset()
        for agent in env.agent_iter():
            clock.tick(env.metadata["render_fps"])

            observation, reward, termination, truncation, info = env.last()
            
            greedyPolicy = greedy.GreedyPolicy(env, strategy_index)

            #action = env.action_space(agent).sample()
            action = greedyPolicy(observation,agent) #!!! -> esta linha + ficheiro greedy

            if termination or truncation:
                env.step(None)
            else:
                env.step(action)

    strategy_index += 1

# Results is a dictionary: key=case, value=results being plotted
results = {}
for case in OUTPUT_FILES:
    f = open(case, 'r')

    # Example = plot the frame number they survive
    all_frames = []
    for episode in f.readlines():
        resultJSON = json.loads(episode)
        all_frames += [resultJSON["total_kills"]]

    all_frames = np.array(all_frames)
    results[case] = all_frames

graph_utils.compare_results(
    results,
    title="Comparion between number of total_kills",
    colors=COLORS
)