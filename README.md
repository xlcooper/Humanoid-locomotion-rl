# Humanoid Locomotion RL

MaMuJoCo Humanoid 单智能体连续控制实验项目，包含手写 PPO baseline 与 Stable-Baselines3 SAC 强基线对比。

本仓库保留实验代码、复现命令、结果摘要和展示素材入口，面向项目展示与实验复现。训练产物中的 checkpoint、replay buffer、TensorBoard event、raw log 和完整视频不纳入仓库。

## 项目简介

Humanoid 是 MuJoCo 中经典的高维连续控制 locomotion 任务。智能体通过连续关节力矩控制类人机器人保持平衡并向前移动。相比 CartPole、Pendulum 等低维控制任务，Humanoid 的 observation/action space 更大，身体动力学更复杂，训练中更容易暴露 critic 拟合压力、策略更新不稳定、动作越界和高 reward 行为不自然等问题。

本项目基于 Farama Gymnasium-Robotics 的 MaMuJoCo Humanoid 环境，使用 `partitioning=None`，将完整 Humanoid 作为单智能体连续控制任务。实验流程覆盖环境适配、手写 PPO、训练诊断、消融优化、TensorBoard 监控、视频检查，以及与 SB3 SAC off-policy 强基线的对比。

## 实验内容

- MaMuJoCo Humanoid 单智能体环境封装，底层来自 PettingZoo Parallel API。
- 手写 PPO：GAE、clipped objective、value loss、entropy logging、checkpoint、deterministic evaluation。
- PPO 诊断指标：observation normalization、approx KL、clip fraction、action clipping fraction、action log std。
- tanh-squashed Gaussian policy：将策略输出约束到环境动作范围，并对 log probability 加入 Jacobian correction。
- SB3 SAC baseline：`VecNormalize`、`Monitor`、自动熵调节、checkpoint、evaluation、TensorBoard 和视频渲染。
- 结果摘要：PPO 三 seed final baseline 与 SAC `1M` seed `0` baseline。

## 结果摘要

### PPO Final Baseline

最终 PPO 配置：

- 实现方式：手写 PPO
- 环境：MaMuJoCo Humanoid, `partitioning=None`
- 训练步数：每个 seed `3M` timesteps
- observation normalization：开启
- policy：tanh-squashed Gaussian
- PPO update epochs：`4`
- evaluation：deterministic policy，每个 seed 10 个 episode

| Seed | Evaluation Mean Return | Evaluation Std | Tail Action Clip Fraction |
| ---: | ---: | ---: | ---: |
| 0 | 716.011 | 115.490 | 0.0000 |
| 1 | 899.806 | 190.234 | 0.0000 |
| 2 | 861.418 | 122.380 | 0.0000 |

三 seed evaluation mean return：

```text
825.745
```

### SAC Strong Baseline

SAC 配置：

- 实现方式：Stable-Baselines3 SAC
- 环境：同一个 MaMuJoCo Humanoid 单智能体任务
- 训练步数：`1M` timesteps
- seed：`0`
- observation normalization：SB3 `VecNormalize(norm_obs=True, norm_reward=False)`
- entropy coefficient：自动调节
- evaluation：deterministic policy，10 个 episode

```text
mean_return=6042.360
std_return=37.329
mean_length=1000.000
```

SAC seed `0` 的 10 个 evaluation episode 全部达到 `1000` step 时间上限，形成了本项目的强 off-policy 对照。SAC 结果来自单 seed，稳定性结论仍以 PPO 三 seed baseline 为主。

## TensorBoard 与视频

展示素材目录：

```text
assets/
  figures/
    ppo_final_seed1_tensorboard.png
    sac_1m_seed0_tensorboard.png
  videos/
    sac_1m_seed0_episode_003.mp4
```

图表内容：

- PPO final seed `1` TensorBoard：episode return/length、value loss、entropy、approximate KL、clip fraction、action clipping diagnostics。
- SAC `1M` seed `0` TensorBoard：`rollout/ep_rew_mean`、`rollout/ep_len_mean`、`train/actor_loss`、`train/critic_loss`、`train/ent_coef`、`train/ent_coef_loss`。

视频观察显示，SAC seed `0` 能够稳定移动并获得较高 reward，但姿态明显前倾、屈身，不接近自然人类步态。因此该结果描述为 reward-driven locomotion，而不是自然步态生成。

## 仓库结构

```text
.
├── src/
│   ├── envs.py                 # MaMuJoCo 单智能体环境封装
│   ├── ppo.py                  # PPO 网络、buffer 和 update 逻辑
│   ├── normalization.py        # Running mean/std observation normalization
│   ├── train_ppo.py            # 手写 PPO 训练入口
│   ├── evaluate.py             # PPO deterministic evaluation
│   ├── render_policy.py        # PPO 视频渲染
│   ├── train_sac_sb3.py        # SB3 SAC 训练入口
│   ├── evaluate_sac_sb3.py     # SB3 SAC deterministic evaluation
│   ├── render_sac_sb3.py       # SB3 SAC 视频渲染
│   └── check_mamujoco_env.py   # MaMuJoCo 环境 smoke test
├── scripts/
│   ├── summarize_ppo_run.py
│   └── summarize_sac_run.py
├── results/
│   └── ppo_sac_summary.md
├── docs/
│   └── environment.md
├── assets/
│   ├── figures/
│   └── videos/
├── requirements.txt
├── LICENSE
└── README.md
```

## 环境

实验运行环境见 [docs/environment.md](docs/environment.md)。

```bash
conda create -n humanoid-rl python=3.11
conda activate humanoid-rl
pip install -r requirements.txt
```

环境 smoke test：

```bash
python src/check_mamujoco_env.py --partitioning none --steps 5
```

## 复现实验命令

### PPO Smoke Test

```bash
python src/train_ppo.py \
  --seed 0 \
  --total-timesteps 100000 \
  --run-name ppo_smoke_seed0 \
  --normalize-observations \
  --tensorboard
```

### PPO Final Baseline

```bash
python src/train_ppo.py \
  --seed 0 \
  --total-timesteps 3000000 \
  --rollout-steps 2048 \
  --batch-size 256 \
  --update-epochs 4 \
  --run-name ppo_long_obsnorm_squash_ep4_seed0 \
  --normalize-observations \
  --squash-actions \
  --tensorboard
```

PPO final baseline 使用 seed `0/1/2`。

### SAC Baseline

```bash
python src/train_sac_sb3.py \
  --seed 0 \
  --total-timesteps 1000000 \
  --learning-starts 10000 \
  --batch-size 256 \
  --buffer-size 1000000 \
  --run-name sac_sb3_1m_seed0 \
  --eval-episodes 10 \
  --log-interval 10
```

## Evaluation

### PPO

```bash
python src/evaluate.py \
  --checkpoint /root/autodl-tmp/Humanoid-runs/ppo_long_obsnorm_squash_ep4_seed0/checkpoints/agent_final.pt \
  --episodes 10
```

### SAC

```bash
python src/evaluate_sac_sb3.py \
  --checkpoint /root/autodl-tmp/Humanoid-runs/sac_sb3_1m_seed0/checkpoints/sac_final.zip \
  --vecnormalize /root/autodl-tmp/Humanoid-runs/sac_sb3_1m_seed0/vecnormalize.pkl \
  --episodes 10 \
  --output-json /root/autodl-tmp/Humanoid-runs/sac_sb3_1m_seed0/eval_results.json
```

## 视频渲染

### PPO

```bash
python src/render_policy.py \
  --checkpoint /root/autodl-tmp/Humanoid-runs/ppo_long_obsnorm_squash_ep4_seed1/checkpoints/agent_final.pt \
  --episodes 3
```

### SAC

```bash
python src/render_sac_sb3.py \
  --checkpoint /root/autodl-tmp/Humanoid-runs/sac_sb3_1m_seed0/checkpoints/sac_final.zip \
  --vecnormalize /root/autodl-tmp/Humanoid-runs/sac_sb3_1m_seed0/vecnormalize.pkl \
  --episodes 3
```

## TensorBoard

```bash
tensorboard --logdir /root/autodl-tmp/Humanoid-runs --host 0.0.0.0 --port 6006
```

PPO 关注 episode return/length、value loss、entropy、approximate KL、clip fraction 和 action clipping diagnostics。SAC 中 `rollout/` 曲线反映环境交互表现，`train/` 曲线反映 actor、critic 和 entropy coefficient 的优化过程。

## 局限

- PPO 已完成 seed `0/1/2` 三 seed 验证；SAC 结果来自 seed `0`。
- 高 reward 不等于自然步态，连续控制结果需要结合视频检查策略行为。
- 仓库不包含 checkpoint、replay buffer、raw logs、TensorBoard event 文件和完整视频产物。
- 本实验只覆盖 MaMuJoCo Humanoid 单智能体任务，多智能体 partitioning 未纳入本仓库。

## License

本项目使用 MIT License。
