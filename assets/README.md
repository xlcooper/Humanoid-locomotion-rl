# Assets

本目录用于存放 README 或展示页面引用的小体积素材。

```text
figures/    # 压缩后的图表、截图，适合直接嵌入 README
videos/     # 短视频片段，适合在 README 中链接或嵌入
```

当前素材：

```text
figures/PPO_tb1.png
figures/PPO_tb2.png
figures/SAC_tb1.png
figures/SAC_tb2.png
videos/PPO.mp4
videos/SAC.mp4
```

`SAC_tb1.png` 当前与 `PPO_tb2.png` 内容相同，暂不在根 README 中展示；如有正确的 SAC 图表，可以替换该文件或新增更明确的文件名。

`results/` 用于保存文字、表格和指标摘要，不建议放图片或视频。完整训练视频、TensorBoard event、raw log、checkpoint 和 replay buffer 不纳入版本管理。
