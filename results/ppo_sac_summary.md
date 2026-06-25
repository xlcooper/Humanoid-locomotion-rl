# PPO/SAC 结果摘要

本文件汇总 MaMuJoCo Humanoid 单智能体实验的核心结果。

## 任务设置

- 任务：MaMuJoCo Humanoid
- 控制方式：单智能体连续控制
- partitioning：`None`
- observation 维度：`348`
- action 维度：`17`

## PPO Final Baseline

最终 PPO 配置：

- 实现方式：手写 PPO
- observation normalization：开启
- policy：tanh-squashed Gaussian
- update epochs：`4`
- 训练步数：每个 seed `3M` timesteps
- evaluation：每个 seed 10 个 episode

| Seed | Evaluation Mean Return | Evaluation Std |
| ---: | ---: | ---: |
| 0 | 716.011 | 115.490 |
| 1 | 899.806 | 190.234 |
| 2 | 861.418 | 122.380 |

三 seed evaluation mean return：

```text
825.745
```

主要结论：

- observation normalization 降低了 critic 拟合压力，并改善了训练稳定性。
- 原始 Gaussian policy 在长训后出现严重动作越界，环境端裁剪比例很高。
- tanh-squashed Gaussian policy 将 action clipping fraction 从约 `98.26%` 降到 `0.00%`。
- `update_epochs=4` 比 `update_epochs=10` 更适合该 squashed PPO baseline。

## SB3 SAC Baseline

SAC 配置：

- 实现方式：Stable-Baselines3
- 训练步数：`1M` timesteps
- seed：`0`
- observation normalization：`VecNormalize(norm_obs=True, norm_reward=False)`
- entropy coefficient：自动调节
- evaluation：10 个 episode

Evaluation 输出：

```text
episode=1 return=6086.414 length=1000
episode=2 return=6043.676 length=1000
episode=3 return=6016.683 length=1000
episode=4 return=6070.044 length=1000
episode=5 return=6017.678 length=1000
episode=6 return=6075.439 length=1000
episode=7 return=6035.541 length=1000
episode=8 return=6097.653 length=1000
episode=9 return=5977.473 length=1000
episode=10 return=6003.000 length=1000
mean_return=6042.360 std_return=37.329
mean_length=1000.000
```

主要结论：

- 10 个 deterministic evaluation episode 全部达到 `1000` step 时间上限。
- SAC seed `0` 的回报显著高于 PPO final baseline。
- 视频结果显示策略能够稳定移动，但姿态前倾、屈身，不属于自然人类步态。
- SAC 结果来自单 seed，未形成多 seed 稳定性结论。

## 展示素材

README 展示素材位于：

```text
assets/figures/PPO_tb1.png
assets/figures/PPO_tb2.png
assets/figures/SAC_tb2.png
assets/videos/PPO.mp4
assets/videos/SAC.mp4
```

`assets/figures/SAC_tb1.png` 当前与 `PPO_tb2.png` 内容相同，暂不作为结果图展示。完整训练视频、TensorBoard event 和 raw log 不纳入版本管理。
