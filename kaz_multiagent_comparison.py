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
OUTPUT_FILES=[const.STRATEGY_LIST[0]+".txt", const.STRATEGY_LIST[1]+".txt", const.STRATEGY_LIST[2]+".txt"]

METRICS=["Frames", "Total Kills", "Archer Kills", "Knight Kills", "Agent_Deaths"]
COLORS=["purple", "red", "green", "blue", "yellow"]

def plot_metrics_graph(results):
    """Creates a bar plot for comparing different agents/teams.

    Parameters
    ----------

    names: Sequence[str]
        A sequence of names (representing either the agent names or the team names)
    means: Sequence[float]
        A sequence of means (one mean for each name)
    std_devs: Sequence[float]
        A sequence of standard deviations (one for each name)
    N: Sequence[int]
        A sequence of sample sizes (one for each name)
    title: str
        The title of the plot
    x_label: str
        The label for the x-axis (e.g. "Agents" or "Teams")
    y_label: str
        The label for the y-axis
    confidence: float
        The confidence level for the confidence interval
    show: bool
        Whether to show the plot
    filename: str
        If given, saves the plot to a file
    colors: Optional[Sequence[str]]
        A sequence of colors (one for each name)
    yscale: str
        The scale for the y-axis (default: linear)
    """

    # X = ['Group A','Group B','Group C','Group D']
    # Ygirls = [10,20,20,40]
    # Zboys = [20,30,25,30]

    names = list(results.keys())
    X_axis = np.arange(len(names))

    frames_means = []
    
    # Result = [frames, total_kills, archer_kills, knight_kills, agent_deaths] of a case
    for result in results.values():
        caseResults = list(results.values())
        means = [metric.mean() for metric in caseResults[0]]
        stds = [metric.std() for metric in caseResults[0]]
        N = [metric.size for metric in caseResults[0]]

        frames_means += [means[0]]

    i = 0
    for metric in METRICS:

        means = []
        stds = []
        N = []

        for result in list(results.values()):
            means += [result[i].mean()]
            stds += [result[i].std()]
            N += [result[i].size]

        i += 1

        plt.bar(X_axis + i, means, 0.4, label = metric)
    
    
    # means = [result.mean() for result in results.values()]
    # stds = [result.std() for result in results.values()]
    # N = [result.size for result in results.values()]
    # plot_confidence_bar(
    #     names=names,
    #     means=means,
    #     std_devs=stds,
    #     N=N,
    #     title=title,
    #     x_label="", y_label=f"Avg. {metric}",
    #     confidence=confidence, show=True, colors=colors
    # )
    
    # plt.bar(X_axis - 0.2, frames_means, 0.4, label = 'Girls')
    # plt.bar(X_axis + 0.2, Zboys, 0.4, label = 'Boys')
    
    plt.xticks(X_axis, names)
    plt.xlabel("Groups")
    plt.ylabel("Number of Students")
    plt.title("Number of Students in each group")
    plt.legend()
    plt.show()

    # yscale = None
    # filename = None
    # show = True
    # x_label = ""
    # y_label = "Avg"
    # title = "Hahayes"
    # errors = [graph_utils.standard_error(stds[i], N[i], 0.95) for i in range(len(means))]
    # print(errors)
    # fig, ax = plt.subplots()
    # x_pos = np.arange(len(names))
    # ax.bar(x_pos, means, yerr=errors, align='center', alpha=0.5, color=COLORS if COLORS is not None else "gray", ecolor='black', capsize=10)
    # ax.bar(x_pos, means, yerr=errors, align='center', alpha=0.5, color="gray", ecolor='black', capsize=10)
    # ax.set_ylabel(y_label)
    # ax.set_xlabel(x_label)
    # ax.set_xticks(x_pos)
    # ax.set_xticklabels(names)
    # ax.set_title(title)
    # ax.yaxis.grid(True)
    # if yscale is not None:
    #     plt.yscale(yscale)
    # plt.tight_layout()
    # if filename is not None:
    #     plt.savefig(filename)
    # if show:
    #     plt.show()
    # plt.close()

# Delete result files from previous executions
# for name in OUTPUT_FILES:
#     if os.path.exists(name):
#         os.remove(name)

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
    break;
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

    frames = []
    total_kills = []
    archer_kills = []
    knight_kills = []
    agent_deaths = []
    for episode in f.readlines():
        resultJSON = json.loads(episode)
        frames += [resultJSON["frames"]]
        total_kills += [resultJSON["total_kills"]]
        archer_kills += [resultJSON["archer_kills"]]
        knight_kills += [resultJSON["knight_kills"]]
        agent_deaths += [resultJSON["dead_agents"]]

    frames = np.array(frames)
    total_kills = np.array(total_kills)
    archer_kills = np.array(archer_kills)
    knight_kills = np.array(knight_kills)
    agent_deaths = np.array(agent_deaths)

    results[case] = [frames, total_kills, archer_kills, knight_kills, agent_deaths]

plot_metrics_graph(results)

# graph_utils.compare_results(
#     results,
#     title="Comparion between number of total_kills",
#     colors=COLORS
# )