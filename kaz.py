import pygame
import knights_archers_zombies
import greedy

env = knights_archers_zombies.env(render_mode="human",
    spawn_rate=20,
    num_archers=3,
    num_knights=3,
    max_zombies=10, 
    max_arrows=10,
    killable_knights=True,
    killable_archers=True,
    pad_observation=False,
    line_death=False,
    max_cycles=900,
    vector_state=True,
    use_typemasks=False)
env.reset()

clock = pygame.time.Clock()

for agent in env.agent_iter():
    clock.tick(env.metadata["render_fps"])

    observation, reward, termination, truncation, info = env.last()
    
    greedyPolicy = greedy.GreedyPolicy(env)

    #action = env.action_space(agent).sample()
    action = greedyPolicy(observation,agent) #!!! -> esta linha + ficheiro greedy

    if termination:
        env.step(None)
    else:
        env.step(action)
