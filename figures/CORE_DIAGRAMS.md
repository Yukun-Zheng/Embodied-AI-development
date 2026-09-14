# Core Mechanism Diagrams

> 全书共用图谱。所有图使用 Mermaid，GitHub 可直接渲染。原则：**先画系统、变量、时间与 frame，再讲公式。**

---

# Figure 1 — Embodied Intelligence Closed Loop

```mermaid
flowchart TD
    W[Physical World]
    S[Sensors]
    O[Observation]
    B[Belief / State / Representation]
    M[Memory]
    WM[World Model / Prediction]
    R[Reasoning / Planning]
    P[Policy / Action Generator]
    E[Temporal Executor]
    C[IK / WBC / Controller / Safety]
    A[Actuator / Robot Body]
    X[Experience / Failure / Evaluation]
    L[Learning / Consolidation]

    W --> S --> O --> B
    B <--> M
    B --> WM --> R --> P --> E --> C --> A --> W
    B --> R
    A --> X
    W --> X
    X --> L
    L --> M
    L --> P
    L --> WM
```

核心问题不是：

```text
input → model → output
```

而是：

```text
world → sensing → internal state → decision → physical action → changed world → new evidence
```

---

# Figure 2 — Policy Output Is Not Motor Torque by Default

```mermaid
flowchart LR
    OBS[Observation]
    PI[Policy / VLA]
    REP[Action Representation]
    IK[IK / Task-Space Mapping]
    CTRL[PID / Impedance / WBC]
    LIM[Safety Limits]
    ACT[Actuator]
    WORLD[Physical World]

    OBS --> PI --> REP --> IK --> CTRL --> LIM --> ACT --> WORLD
```

同一个“7-D action”可能是：

- Cartesian delta；
- target pose；
- joint delta；
- action token 解码结果。

如果 controller stack 不同，不能把 success 差异全归因于 policy。

---

# Figure 3 — Coordinate-Frame Chain

```mermaid
flowchart LR
    CAM[Camera frame C]
    BASE[Robot base B]
    WORLD[World W]
    EE[End-effector E]
    OBJ[Object O]

    CAM -- T_BC --> BASE
    BASE -- T_WB --> WORLD
    EE -- T_BE --> BASE
    OBJ -- T_CO --> CAM
```

典型组合：

\[
T_{WO}=T_{WB}T_{BC}T_{CO}.
\]

任何 perception → action 系统都应明确每个 tensor 属于哪个 frame。

---

# Figure 4 — Multi-Rate Robot System

```mermaid
flowchart TD
    LLM[Reasoner / Planner<br/>0.1–5 Hz]
    VLA[VLA / Large Policy<br/>2–30 Hz]
    EST[State Estimator<br/>100–1000 Hz]
    WBC[WBC / Task Controller<br/>100–500 Hz]
    SERVO[Joint Servo<br/>500–2000 Hz]
    MOTOR[Motor Current Loop<br/>kHz]
    SENS[Camera / IMU / Joint Sensors]

    LLM --> VLA --> WBC --> SERVO --> MOTOR
    SENS --> EST --> VLA
    EST --> WBC
```

频率仅为常见量级示意，不是统一标准。重点是：**语义、policy、稳定控制不需要共用一个 clock。**

---

# Figure 5 — Classical Manipulator Mathematics

```mermaid
flowchart LR
    Q[Joint q]
    FK[Forward Kinematics]
    X[End-Effector Pose T]
    J[Jacobian J(q)]
    V[Twist V]
    DYN[Dynamics M,C,g]
    TAU[Torque τ]

    Q --> FK --> X
    Q --> J
    J --> V
    Q --> DYN
    TAU --> DYN
```

核心关系：

\[
V=J(q)\dot q,
\]

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J^T\lambda.
\]

---

# Figure 6 — State Estimation vs Raw Observation

```mermaid
flowchart LR
    RGB[RGB / Depth]
    IMU[IMU]
    ENC[Joint Encoders]
    FT[Force / Tactile]
    CAL[Calibration + Timestamp]
    FILTER[Bayes / Kalman / Factor Graph]
    BELIEF[Belief / State + Uncertainty]

    RGB --> CAL
    IMU --> CAL
    ENC --> CAL
    FT --> CAL
    CAL --> FILTER --> BELIEF
```

机器人真正用于决策的通常不是原始 sensor packet，而是带时空语义与不确定性的内部 state/belief。

---

# Figure 7 — Active Perception as Decision Under Information Value

```mermaid
flowchart TD
    B[Current Belief]
    U[Uncertainty]
    CAND[Candidate View / Touch Actions]
    IG[Expected Information Gain]
    COST[Motion / Time / Risk Cost]
    SELECT[Select Information Action]
    SENSE[Acquire New Observation]
    B2[Updated Belief]

    B --> U --> CAND
    CAND --> IG
    CAND --> COST
    IG --> SELECT
    COST --> SELECT
    SELECT --> SENSE --> B2
```

目标可抽象为：

\[
a^*=\arg\max_a \mathbb E[IG(a)]-\lambda C(a).
\]

---

# Figure 8 — Imitation Learning and DAgger

```mermaid
flowchart TD
    DEMO[Expert Demonstrations]
    BC[Behavior Cloning]
    POL[Learned Policy]
    ROLL[Policy Rollout]
    SHIFT[Visited OOD States]
    QUERY[Query Expert]
    AGG[Aggregate Dataset]

    DEMO --> BC --> POL --> ROLL --> SHIFT --> QUERY --> AGG --> BC
```

BC 的核心问题不是训练 loss，而是 policy 改变了自己未来访问的 state distribution。

---

# Figure 9 — Three Action-Generation Paradigms

```mermaid
flowchart TD
    CTX[Vision / Language / State Context]

    AR[Autoregressive Action Tokens]
    DIFF[Diffusion Action Trajectory]
    FLOW[Flow-Matching Action Expert]

    TOK[Discrete Tokens]
    TRAJ1[Continuous Chunk]
    TRAJ2[Continuous Chunk]

    CTX --> AR --> TOK
    CTX --> DIFF --> TRAJ1
    CTX --> FLOW --> TRAJ2
```

三者最大的差异是**动作表示与生成过程**，而不是是否使用 Transformer。

---

# Figure 10 — Modern VLA Stack

```mermaid
flowchart TD
    IMG[Images / Video]
    LANG[Language]
    STATE[Proprioception]
    EMB[Embodiment]
    BACK[Multimodal Backbone]
    HEAD[Action Tokens / Diffusion / Flow / DiT]
    CHUNK[Action Chunk]
    EXEC[Queue / Receding Horizon / Async / RTC]
    CTRL[Robot Controller]

    IMG --> BACK
    LANG --> BACK
    STATE --> BACK
    EMB --> BACK
    BACK --> HEAD --> CHUNK --> EXEC --> CTRL
```

对 2026 VLA 的研究不能只停在 `BACK → HEAD`。

---

# Figure 11 — Action Token vs Continuous Expert

```mermaid
flowchart LR
    A[Continuous Robot Action]
    Q[Quantizer]
    TOK[Action Tokens]
    LM[AR VLM]
    DQ[De-tokenize]

    N[Noise]
    VEL[Continuous Vector Field]
    INT[ODE / Euler Integration]
    CHUNK[Action Trajectory]

    A --> Q --> TOK --> LM --> DQ
    N --> VEL --> INT --> CHUNK
```

OpenVLA 类路线主要承担 quantization + token prediction error；flow 路线主要承担 vector-field + numerical-integration error。

---

# Figure 12 — Temporal Executor and Stale Action

```mermaid
flowchart TD
    O0[Observation at t0]
    INF[Model Inference τ]
    CHUNK[Predicted Chunk]
    OLD[Previous Executing Chunk]
    QUEUE[Action Queue]
    RTC[RTC / Overlap Guidance]
    ROBOT[Robot]

    O0 --> INF --> CHUNK
    OLD --> QUEUE --> ROBOT
    CHUNK --> QUEUE
    OLD --> RTC
    CHUNK --> RTC --> ROBOT
```

当：

\[
\tau_{inference}>\Delta t_{action},
\]

模型产生的动作在执行时已经基于旧世界状态。RTC / async execution 是系统问题，不是纯网络结构问题。

---

# Figure 13 — World Model Used for Control

```mermaid
flowchart LR
    Z[Current State / Latent]
    CAND[Candidate Action Sequences]
    WM[Action-Conditioned World Model]
    FUT[Predicted Futures]
    COST[Evaluator / Reward / Constraint]
    SEL[Choose Best Sequence]
    EXE[Execute First Action]
    OBS[Observe Again]

    Z --> CAND --> WM --> FUT --> COST --> SEL --> EXE --> OBS --> Z
```

判断 world model 是否有用的关键不是 prediction loss，而是：

\[
J_{policy+WM}>J_{policy-no-WM}.
\]

---

# Figure 14 — Memory Is Not the Same as World Model

```mermaid
flowchart TD
    OBS[Current Observation]
    STM[Short-Term Sensorimotor Memory]
    EPI[Episodic Memory]
    SEM[Semantic Memory]
    SPAT[Spatial Memory]
    RET[Retriever]
    POL[Reasoner / Policy]
    WM[World Model]

    OBS --> STM
    STM --> RET
    EPI --> RET
    SEM --> RET
    SPAT --> RET
    RET --> POL
    OBS --> WM --> POL
```

Memory回答“过去发生了什么 / 什么长期存在”；world model回答“如果做动作，未来可能怎样变化”。

---

# Figure 15 — Humanoid Whole-Body Stack

```mermaid
flowchart TD
    GOAL[Task / Language Goal]
    HIGH[High-Level VLA / Planner]
    MOTION[Whole-Body Motion / Target]
    WBC[WBC / HQP / Motor Policy]
    CONTACT[Contact / Balance Manager]
    SERVO[Joint Servo]
    BODY[Humanoid Body]
    EST[IMU + Proprio + Vision Estimator]

    GOAL --> HIGH --> MOTION --> WBC --> CONTACT --> SERVO --> BODY
    BODY --> EST --> HIGH
    EST --> WBC
```

whole-body VLA 并不意味着 WBC、balance、servo 消失。

---

# Figure 16 — Cross-Embodiment Intelligence

```mermaid
flowchart TD
    TASK[Task / Effect Goal]
    SHARED[Shared Semantic / Skill Representation]
    EMB[Embodiment Descriptor]
    DEC[Embodiment-Conditioned Decoder]
    A1[Robot A Action Space]
    A2[Robot B Action Space]
    A3[Robot C Action Space]

    TASK --> SHARED
    EMB --> DEC
    SHARED --> DEC
    DEC --> A1
    DEC --> A2
    DEC --> A3
```

跨本体的核心不是把不同 joint vector 直接 padding，而是找到哪些能力应共享、哪些必须由身体条件化。

---

# Figure 17 — Continual / Developmental Learning Loop

```mermaid
flowchart TD
    WORLD[Current Environment]
    EXP[Interaction Experience]
    FAIL[Failure / Surprise]
    MEM[Memory / Replay]
    UPDATE[Parameter / Structure Update]
    RET[Retention Evaluation]
    FT[Forward Transfer]
    NEXT[New Environment / Body / Task]

    WORLD --> EXP --> FAIL --> MEM --> UPDATE --> RET --> FT --> NEXT --> EXP
```

真正的 self-evolving system 必须同时记录：

\[
\text{new capability},
\quad
\text{retention},
\quad
\text{forward transfer},
\quad
\text{resource growth}.
\]

只增加参数或训练更多步不等于“发展”。

---

# Figure 18 — Scientific Research Loop

```mermaid
flowchart LR
    Q[Question]
    H[Hypothesis]
    M[Mechanism]
    MIN[Minimal Experiment]
    NEG[Negative Control]
    F[Failure Analysis]
    SCALE[Scale Up]
    GEN[Generalize / Theory]

    Q --> H --> M --> MIN --> NEG --> F --> SCALE --> GEN
    F --> H
```

这张图是全书研究方法的最终闭环：**先让机制可证伪，再花大算力。**

---

# Figure usage rule

引用这些图时，不要只复制视觉布局。正文还应写清：

- 每个节点对应哪些变量 / tensor；
- 每条边的方向、频率和 frame；
- 哪些模块 trainable / frozen；
- 哪些是模型，哪些是 robot runtime；
- failure 最可能发生在哪条边。

一张真正有用的系统图必须能指导代码追踪和实验设计。
