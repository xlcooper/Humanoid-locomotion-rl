# 实验环境

训练和评估运行在 AutoDL Linux 服务器上，开发侧负责代码编辑、Git 管理和结果分析。以下配置对应本项目的主要实验环境。

## 服务器配置

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Ubuntu 22.04.5 LTS |
| CPU | Intel Xeon Platinum 8470，104 物理核心 / 208 逻辑线程 |
| 内存 | 754 GiB total |
| GPU | NVIDIA GeForce RTX 5090 D，32607 MiB |
| NVIDIA Driver | 595.71.05 |
| CUDA 兼容版本 | 13.2，来自 `nvidia-smi` |
| Conda | 24.4.0 |
| Python | 3.11.15 |

## 关键 Python 包

| 包 | 版本 |
| --- | --- |
| torch | 2.12.1+cu130 |
| gymnasium | 1.3.0 |
| gymnasium_robotics | 1.4.2 |
| mujoco | 3.9.0 |
| pettingzoo | 1.26.1 |
| tensorboard | 2.20.0 |

## 运行产物

训练产物位于服务器数据盘：

```text
/root/autodl-tmp/Humanoid-runs/
```

仓库只保留代码、结果摘要和少量展示素材。checkpoint、raw log、replay buffer、TensorBoard event 和完整视频不纳入版本管理。
