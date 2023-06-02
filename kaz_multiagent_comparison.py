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

N_CASES=2
N_EPISODES=3
OUTPUT_FILES=["CASE1.txt", "CASE2.txt"]
COLORS=["green", "blue"]

# Delete result files from previous executions
for name in OUTPUT_FILES:
    if os.path.exists(name):
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

# Results is a dictionary: key=case, value=results being plotted
results = {}
for case in OUTPUT_FILES:
    f = open(case, 'r')

    # Example = plot the frame number they survive
    all_frames = []
    for episode in f.readlines():
        resultJSON = json.loads(episode)
        all_frames += [resultJSON["frames"]]

    all_frames = np.array(all_frames)
    results[case[:len(case)-4]] = all_frames

graph_utils.compare_results(
    results,
    title="Comparion between number of frames survived",
    colors=COLORS
)