import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from constants.global_var import config
config.use_opengl = False
config.apply_controller_vibration = False

import numpy as np

from sb3_contrib import RecurrentPPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList, BaseCallback

from reinforcement_learning.ai_env import ShootEmUpEnv


class VecNormalizeSaveCallback(BaseCallback):
    def __init__(self, save_freq, save_path, verbose=0):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path

    def _on_step(self) -> bool:
        if self.num_timesteps % self.save_freq == 0:
            path = os.path.join(self.save_path, "vecnormalize.pkl")
            self.training_env.save(path)
            if self.verbose:
                print(f"[VecNormalize] saved to {path}")
        return True


def make_stage_env(stage, n_envs):
    return make_vec_env(
        ShootEmUpEnv,
        n_envs=n_envs,
        vec_env_cls=SubprocVecEnv,
        env_kwargs=dict(stage=stage, frame_skip=3),
    )


def wrap_vecnormalize(env, path):
    if os.path.exists(path):
        print(f"Loading existing VecNormalize from {path}")
        env = VecNormalize.load(path, env)
        env.training = True
        env.norm_reward = True
    else:
        env = VecNormalize(
            env,
            norm_obs=True,
            norm_reward=True,
            clip_obs=10.0,
            clip_reward=10.0,
            gamma=0.995,
        )
    return env


def main():
    models_dir = "models/PPO_LSTM"
    log_dir = "logs_lstm"

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    n_envs = 8

    curriculum = [
        ("movement", 60_000),
        ("single_enemy", 80_000),
        ("swarm", 120_000),
        ("boss", 80_000),
        ("full", 200_000),
    ]

    vecnorm_path = os.path.join(models_dir, "vecnormalize.pkl")
    model_path = os.path.join(models_dir, "model_lstm.zip")

    model = None

    print("Starting training with RecurrentPPO...")

    for stage, timesteps in curriculum:
        print(f"\n=== Stage: {stage} | timesteps: {timesteps} ===")

        env = make_stage_env(stage, n_envs)
        env = wrap_vecnormalize(env, vecnorm_path)

        if model is None:
            model = RecurrentPPO(
                "MlpLstmPolicy",
                env,
                verbose=1,
                tensorboard_log=log_dir,
                n_steps=256,
                batch_size=64,
                gamma=0.995,
                gae_lambda=0.95,
                learning_rate=3e-4,
                ent_coef=0.01,
                clip_range=0.2,
            )
        else:
            model.set_env(env)

        checkpoint_callback = CheckpointCallback(
            save_freq=max(10_000 // n_envs, 1),
            save_path=models_dir,
            name_prefix=f"model_{stage}"
        )

        vecnorm_callback = VecNormalizeSaveCallback(
            save_freq=10_000,
            save_path=models_dir,
            verbose=1
        )

        callbacks = CallbackList([checkpoint_callback, vecnorm_callback])

        try:
            model.learn(
                total_timesteps=timesteps,
                callback=callbacks,
                progress_bar=True,
                reset_num_timesteps=False
            )
        except KeyboardInterrupt:
            print("\nTraining interrupted manually.")
            break

        model.save(model_path)
        env.save(vecnorm_path)
        env.close()

    print("\nTraining completed!")
    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    main()