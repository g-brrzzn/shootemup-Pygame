import os
import pygame
import random

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from reinforcement_learning.ai_env import ShootEmUpEnv
from Game import screen, game_surface, shader_manager, clock
from game_engine import g_engine


def main():
    model_path = "models/PPO_LSTM/model_lstm.zip"
    vecnormalize_path = "models/PPO_LSTM/vecnormalize.pkl"

    if not os.path.exists(model_path):
        print(f"ERRO: Modelo não encontrado em {model_path}!")
        return

    if not os.path.exists(vecnormalize_path):
        print(f"ERRO: VecNormalize não encontrado em {vecnormalize_path}!")
        return

    print("Carregando o cérebro artificial...")

    # Um único ambiente para jogar
    env = make_vec_env(
        ShootEmUpEnv,
        n_envs=1,
        vec_env_cls=DummyVecEnv
    )

    env = VecNormalize.load(vecnormalize_path, env)
    env.training = False
    env.norm_reward = False

    model = PPO.load(model_path, env=env)

    obs = env.reset()

    print("Iniciando a simulação...")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, infos = env.step(action)

        pygame.display.set_caption(f"Shoot 'em Up IA Jogando - FPS: {int(clock.get_fps())}")

        if not shader_manager:
            game_surface.fill((0, 0, 0, 0))

        # Acesse o ambiente real para desenhar
        real_env = env.venv.envs[0]

        # Descasca wrappers (Monitor, etc)
        while hasattr(real_env, "env"):
            real_env = real_env.env
        real_env.game.draw(game_surface)

        render_offset = [0, 0]
        if g_engine.screen_shake > 0:
            g_engine.screen_shake -= 1
            render_offset[0] = random.randint(-4, 4)
            render_offset[1] = random.randint(-4, 4)

        if shader_manager:
            shader_manager.draw(offset=render_offset)
        else:
            scaled_surface = pygame.transform.scale(game_surface, screen.get_size())
            screen.blit(scaled_surface, render_offset)

        pygame.display.flip()
        clock.tick(g_engine.fps_limit)

        if dones[0]:
            print(f"A IA morreu! Pontuação alcançada: {g_engine.score}. Reiniciando...")
            obs = env.reset()

    pygame.quit()


if __name__ == "__main__":
    main()