import pygame
import knights_archers_zombies
import greedy

from src import constants as const

env = knights_archers_zombies.env(render_mode="human",
    spawn_rate=const.SPAWN_RATE,
    num_archers=const.NUM_ARCHERS,
    num_knights=const.NUM_KNIGHTS,
    max_zombies=const.MAX_ZOMBIES, 
    max_arrows=const.MAX_ARROWS,
    killable_knights=True,
    killable_archers=True,
    pad_observation=False,
    line_death=False,
    max_cycles=const.MAX_CYCLES,
    vector_state=True,
    use_typemasks=False,
    terminal_results=False,
    output_file="results.txt",
    )
env.reset()

clock = pygame.time.Clock()

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
