# Embodied Intelligence Timeline — 1948–2026

> 这不是“谁先发论文”的荣誉榜，而是用于理解**研究问题如何迁移**的技术谱系。年份表示代表性公开节点；同一思想通常有更早前史和并行发展。

---

# 1940s–1960s　反馈、控制与机器智能的源头

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 1948 | Norbert Wiener《Cybernetics》 | 把反馈、控制、通信放进统一框架 |
| 1950 | Turing, “Computing Machinery and Intelligence” | 机器智能讨论进入现代计算时代 |
| 1950s–60s | 工业机械臂与 servo control | 机器人首先成为可控制的物理执行系统 |
| 1961 | Unimate 工业部署 | 机器人进入真实工业生产 |
| 1966–1972 | Shakey | perception → symbolic planning → action 的早期完整 mobile-robot stack |
| 1969 | Whitney resolved-motion-rate control | Jacobian-based differential control 成为经典工具 |

这个时代定义了一个至今未改变的事实：**机器人智能必须闭合在物理反馈环里。**

---

# 1970s–1980s　机器人学的数学骨架形成

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 1970s | manipulator kinematics / dynamics 系统化 | FK、IK、Jacobian、rigid-body dynamics 成为机器人共同语言 |
| 1970s–80s | PUMA / Stanford Arm 等平台 | articulated manipulation 研究成熟 |
| 1980s | impedance / force control | 机器人从“去哪里”扩展到“怎样与世界接触” |
| 1986 | Brooks, Subsumption Architecture | 反击过重的 sense-plan-act，强调 situated / reactive intelligence |
| 1987 | Khatib operational-space formulation | task-space dynamics/control 形成系统方法 |
| 1988 | Bajcsy, Active Perception | perception 被明确视为可主动控制的过程 |

两条思想从此长期并存：

```text
model / plan / optimize
vs
react / interact / exploit embodiment
```

现代具身智能仍在重新组合它们。

---

# 1990s　规划、概率机器人与自主移动成熟

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 1990s | Kalman / particle filter 在机器人系统广泛使用 | uncertainty 进入 state estimation |
| 1996 | PRM | sampling-based motion planning 成熟 |
| 1998 | RRT | 高维运动规划获得非常实用的随机搜索方法 |
| 1990s | probabilistic localization / mapping | belief-based robotics 成为主流 |
| 1990s | grasp mechanics / contact planning 发展 | manipulation 不再只看 kinematics |

这一时期把“机器人不知道自己的状态”从异常变成了数学默认。

---

# 2000s　SLAM、ROS 与现代机器人系统工程

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 2000s | SLAM 大规模发展 | 自主机器人开始长期维护 map / pose belief |
| 2000s | legged / humanoid control 进展 | floating-base、contact、whole-body control 体系发展 |
| 2007–2010 | ROS 形成并广泛使用 | perception/planning/control 逐渐拥有共同软件生态 |
| 2009 | ImageNet | 大规模视觉数据开始重塑 perception |

机器人研究的瓶颈开始从“每个模块都做不出来”转向“如何让很多模块可靠工作在一起”。

---

# 2012–2016　Deep Learning 开始进入机器人

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 2012 | AlexNet / deep vision breakthrough | learned representation 改变机器人感知 |
| 2013–15 | deep RL 重新兴起 | policy/value function 开始由深网表示 |
| 2015 | DDPG | continuous-control deep RL 的代表节点 |
| 2016 | Levine et al. large-scale visuomotor / guided policy search work | end-to-end vision→motor learning 被大规模真机验证 |
| 2016 | domain adaptation / sim-to-real 研究快速增长 | 仿真训练开始成为 robot learning 基础设施 |

关键变化：**手工设计 perception features 开始被 learned representation 替代。**

---

# 2017–2019　Transformer、Sim-to-Real、Dexterity、Benchmark 化

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 2017 | Transformer | 后来成为 VLM/VLA 的主要 backbone |
| 2017 | Domain Randomization | 大规模 randomization 成为 sim-to-real 代表范式 |
| 2018 | SAC | sample-efficient continuous RL 强基线 |
| 2018 | DeepMimic | motion imitation + RL 展示复杂角色运动 |
| 2018–2019 | OpenAI dexterous-hand / Dactyl lineage | 大规模 simulation + RL + domain randomization 进入灵巧操作 |
| 2019 | RLBench | language-described manipulation benchmark 化 |
| 2019 | RoboNet | 多机器人/多任务真实数据 scaling 的早期重要尝试 |

此时已经出现今天很多 foundation robotics 的组成件，但还没有统一在大规模多模态模型中。

---

# 2020–2021　视觉基础模型与更通用的操作表示

| 年代 | 节点 | 长期意义 |
|---|---|---|
| 2020 | Transporter Networks | spatial action representation 在 manipulation 中展示高 data efficiency |
| 2020–21 | offline RL / large replay learning 成熟 | 机器人可以更充分利用已采集 experience |
| 2021 | CLIP | language–vision shared representation 改变 open-vocabulary grounding |
| 2021 | ViT / self-supervised vision scaling | Transformer 与大规模视觉预训练成为主流 |
| 2021 | Habitat 2.0 等 interactive embodied environments | navigation 与 interaction 开始更紧密融合 |

---

# 2022　“Generalist Agent / Language + Robot”转折年

| 节点 | 关键变化 |
|---|---|
| Gato | 把多种任务与 embodiment 都序列化进一个 generalist model |
| SayCan | LLM 高层知识与 robot affordance/value 组合 |
| RT-1 | 大规模真实多任务 robot transformer |
| diffusion-style robot action modeling 开始快速出现 | 多模态连续动作生成成为新路线 |

这一年之后，机器人论文开始越来越频繁使用“generalist”“foundation”“language-conditioned”作为中心概念。

---

# 2023　VLA、生成式策略与低成本双臂迅速汇合

| 节点 | 关键变化 |
|---|---|
| PaLM-E | embodied multimodal language model |
| RT-2 | web-scale vision-language knowledge 映射到 robot action |
| Open X-Embodiment / RT-X | 多实验室、多机器人数据正式规模化 |
| Diffusion Policy | diffusion 成为 visuomotor action distribution 的强范式 |
| ACT / ALOHA | action chunking + low-cost bimanual data 显著推动真实双臂模仿学习 |
| RoboCat | generalist robot policy + self-generated new-task data 的重要节点 |

从这里开始，“数据、backbone、action head、robot fleet”被真正放进同一个 scaling 问题。

---

# 2024　开放 VLA 与 Generalist Policy 生态形成

| 节点 | 关键变化 |
|---|---|
| Octo | 开放 generalist robot policy，强调 cross-dataset/cross-robot |
| OpenVLA | 开放 VLA baseline，进一步降低 foundation-robotics 研究门槛 |
| DROID | in-the-wild 大规模真实 manipulation data |
| π0 | VLM + continuous flow-matching action expert 的代表路线 |
| 3D-aware policies / DP3 等 | point cloud / 3D representation 进入生成式 robot policy 主线 |
| LeRobot ecosystem | dataset/model/evaluation 工具链逐步统一 |

“VLA”从少数大厂系统变成可公开研究的架构类别。

---

# 2025　VLA 开始分化：更实时、更全身、更开放世界、更依赖经验

| 节点 | 关键变化 |
|---|---|
| Gemini Robotics | DeepMind 把 VLA 与 embodied reasoning 更明确结合 |
| GR00T N1 / N1.5 | NVIDIA humanoid foundation model 与 cross-embodiment / post-training 路线 |
| Helix | Figure 提出 slow semantic + fast visuomotor 的 multi-rate humanoid VLA |
| π0.5 | Physical Intelligence 继续推进 open-world generalization |
| Real-Time Action Chunking | action chunking 开始显式解决 stale action / asynchronous inference |
| π*0.6 | foundation policy 开始更直接利用 RL / experience 改善行为 |
| V-JEPA 2 | predictive video representation 与 action-conditioned world model 再度升温 |
| Cosmos | world foundation model / synthetic physical-AI data 平台化 |
| GR00T N1.6 | VLM、DiT、humanoid loco-manipulation 继续扩展 |

重要变化：研究问题开始从“能不能用大模型出动作”转向**实时性、经验学习、whole-body、predictive model 和 deployment**。

---

# 2026　VLA 之后：Memory、Experience、Whole-Body、World Action 与持续发展

> 以下条目以本书冻结时间 **2026-09-14** 为截面。

| 日期/时期 | 节点 | 本书如何理解 |
|---|---|---|
| 2026-01 | Helix 02 | 从上半身/桌面能力推进到 full-body loco-manipulation |
| 2026-03 | Multi-Scale Embodied Memory | VLA 开始显式引入长/短时多尺度记忆，长任务不再只依赖 context window |
| 2026-03 | efficient online RL / RL-token 类方法 | foundation policy + lightweight real-robot experience learning |
| 2026-03 | V-JEPA 2.1 | 更密集、更时间一致的视频预测表征继续向 physical intelligence 靠拢 |
| 2026-04 | π0.7 | steerability、复杂技能组合与 emergent capability 成为新的评价问题 |
| 2026-05 | Cosmos 3 | reasoning、world generation 与 action prediction 更紧密融合 |
| 2026-07 | Gemini Robotics 2 / On-Device 2 | whole-body、dexterity、多机器人、embodied reasoning 与端侧 adaptation 合流 |
| 2026 | SONIC / scalable humanoid motion tracking | humanoid motor foundation / whole-body tracking 的 scaling 路线更加明确 |

截至这一时间点，前沿问题已明显从：

```text
Can a model generate robot actions?
```

转向：

```text
Can it act in real time?
Can it remember?
Can it learn from its own experience?
Can it predict counterfactual physical futures?
Can it coordinate the whole body?
Can it transfer to a new body?
Can it keep improving without forgetting or becoming unsafe?
```

---

# 这条时间线真正告诉我们的三件事

## 1. “新范式”经常是旧问题换了新的计算工具

今天的：

- VLA ↔ perception-action mapping + generalization；
- World Model ↔ model-based control / system identification；
- Active Perception ↔ information gathering；
- Memory ↔ belief / task state / persistent world representation；
- Whole-Body VLA ↔ whole-body control + learned semantic policy。

理解历史能防止把旧问题重新命名成“突然出现的新问题”。

## 2. 但规模确实改变了可研究的问题

大模型、大数据、GPU simulation、foundation representation 让过去无法现实验证的：

- cross-task；
- cross-robot；
- human-video pretraining；
- long-horizon memory；
- general whole-body policy

变成可实验问题。

## 3. 下一阶段更像“长期实体智能”而不是“更大动作模型”

如果把 2026 的多条线放在一起：

```text
VLA
+ Memory
+ World Model
+ Experience Learning
+ Whole-Body
+ Cross-Embodiment
+ Safety
+ Continual Development
```

研究对象正在从“policy”变成一个长期存在、持续更新的**physical agent system**。