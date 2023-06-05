import os
import json
import pygame
import argparse
import numpy as np
from typing import Sequence

import math
from typing import Optional, Sequence
import matplotlib.pyplot as plt

import graph_utils
import knights_archers_zombies
import greedy
from src import constants as const

N_CASES=len(const.STRATEGY_LIST)
N_EPISODES=3
N_GRAPHS=3
OUTPUT_FILES=[const.STRATEGY_LIST[0]+".txt", const.STRATEGY_LIST[1]+".txt", const.STRATEGY_LIST[2]+".txt"]

COLORS=["purple", "red", "green", "blue", "lightsalmon", "palegreen", "powderblue"]

def plot_metrics_graph(results):

    # Names of the cases being studied -> X Axis values
    names = [name[:len(name)-4] for name in list(results.keys())]
    X_axis = np.arange(len(names))

    # Plot 3 bar graphs in  the same row
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 15))

    # Calculate means, std_devs and N_samples for all the metrics in all the cases
    results_means = [[result.mean() for result in list] for list in list(results.values())]
    results_stds = [[result.std() for result in list] for list in list(results.values())]
    results_N = [[result.size for result in list] for list in list(results.values())]

    # Compute 3 graphs
    for idx in range(N_GRAPHS):
        means = []
        stds = []
        N = []

        # Graph 1:  'Frames till Game Over' graph
        if idx == 0:

            # Frames = idx 0 of results 
            for case in results_means:
                means += [case[0]]
            for case in results_stds:
                stds += [case[0]]
            for case in results_N:
                N += [case[0]]

            errors = [graph_utils.standard_error(stds[i], N[i], 0.95) for i in range(len(means))]
            axs[0].bar(X_axis, means, yerr=errors, align='center', alpha=0.5, color=COLORS[0], ecolor='black', capsize=10)
            axs[0].set_ylabel("Frames", fontsize=12)
            axs[0].set_xlabel("Test Cases", fontsize=10)
            axs[0].set_xticks(X_axis)
            axs[0].set_xticklabels(names)
            axs[0].yaxis.grid(True)
            axs[0].set_title("Frames till Game Over", fontsize=14)

        # Graph 2: 'Agent Kills' graph
        if idx == 1:

            # Total/Archer/Knight Kills = idx 1/2/3
            for i in [1,2,3]:

                # Reset for each bar
                means.clear()
                stds.clear()
                N.clear()

                for case in results_means:
                    means += [case[i]]
                for case in results_stds:
                    stds += [case[i]]
                for case in results_N:
                    N += [case[i]]

                # To help arrange the 3 bars
                offsets = [-0.2, 0, 0.2] # 3 side to side bars with width=0.2
                labels = ["Total", "Archers", "Knights"]

                errors = [graph_utils.standard_error(stds[j], N[j], 0.95) for j in range(len(means))]
                axs[1].bar(X_axis+offsets[i-1], means, width=0.2, yerr=errors, align='center',
                           alpha=0.5, color=COLORS[i], ecolor='black', capsize=4, label = labels[i-1])

            axs[1].set_ylabel("Kill Count", fontsize=12)
            axs[1].set_xlabel("Test Cases", fontsize=10)
            axs[1].set_xticks(X_axis)
            axs[1].set_xticklabels(names)
            axs[1].yaxis.grid(True)
            axs[1].legend()
            axs[1].set_title("Number of Zombies Killed", fontsize=14)

        # Graph 3: 'Agent Deaths' graph
        if idx == 2:

            # Total/Archer/Knight Deaths = idx 4/5/6
            for i in [4,5,6]:

                # Reset for each bar
                means.clear()
                stds.clear()
                N.clear()

                for case in results_means:
                    means += [case[i]]
                for case in results_stds:
                    stds += [case[i]]
                for case in results_N:
                    N += [case[i]]

                # To help arrange the 3 bars
                offsets = [-0.2, 0, 0.2] # 3 side to side bars with width=0.2
                labels = ["Total", "Archers", "Knights"]

                errors = [graph_utils.standard_error(stds[j], N[j], 0.95) for j in range(len(means))]
                axs[2].bar(X_axis+offsets[i-4], means, width=0.2, yerr=errors, align='center',
                        alpha=1, color=COLORS[i], ecolor='black', capsize=4, label = labels[i-4])

            axs[2].set_ylabel("Death Count", fontsize=12)
            axs[2].set_xlabel("Test Cases", fontsize=10)
            axs[2].set_xticks(X_axis)
            axs[2].set_xticklabels(names)
            axs[2].yaxis.grid(True)
            axs[2].legend()
            axs[2].set_title("Number of Dead Agents", fontsize=14)
    
    plt.show()
    plt.close()

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

for env, strategy_idx in enumerate(envs): 
    for i in range(N_EPISODES):
        # Reset environment for new episode
        env.reset()
        for agent in env.agent_iter():
            clock.tick(env.metadata["render_fps"])

            observation, reward, termination, truncation, info = env.last()
            
            greedyPolicy = greedy.GreedyPolicy(env, strategy_idx)

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

    frames = []
    total_kills = []
    archer_kills = []
    knight_kills = []
    agent_deaths = []
    archer_deaths = []
    knight_deaths = []
    for episode in f.readlines():
        resultJSON = json.loads(episode)
        frames += [resultJSON["frames"]]
        total_kills += [resultJSON["total_kills"]]
        archer_kills += [resultJSON["archer_kills"]]
        knight_kills += [resultJSON["knight_kills"]]
        agent_deaths += [resultJSON["dead_agents"]]
        archer_deaths += [resultJSON["dead_archers"]]
        knight_deaths += [resultJSON["dead_knights"]]

    frames = np.array(frames)
    total_kills = np.array(total_kills)
    archer_kills = np.array(archer_kills)
    knight_kills = np.array(knight_kills)
    agent_deaths = np.array(agent_deaths)
    archer_deaths = np.array(archer_deaths)
    knight_deaths = np.array(knight_deaths)


    results[case] = [frames, total_kills, archer_kills, knight_kills, agent_deaths, archer_deaths, knight_deaths]

plot_metrics_graph(results)