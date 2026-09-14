# Canonical Figures — 《具身智能：从物理世界到通用机器人》

> 本页收录全书共用的**原创结构图**。全部使用 Mermaid，GitHub 可直接渲染；后续章节插图优先引用或派生自这些图，而不是每章重新发明一套视觉语言。
>
> 设计原则：先画**物理对象与数据流**，再画模型；所有箭头都尽量回答“什么量在流动”。

---

# Figure 1　具身智能的总闭环

```mermaid
flowchart TD
    W[Physical World] --> S[Sensors]
    S --> O[Observation]
    O --> B[State / Belief / Representation]
    B --> WM[Prediction / World Model]
    WM --> R[Reasoning / Planning]
    B --> P[Policy]
    R --> P
    M[Memory / Experience] --> R
    M --> P
    P --> A[Action Representation]
    A --> C[IK / WBC / Controller]
    C --> H[Actuator / Robot Body]
    H --> W
    W --> E[Evaluation / Failure]
    E --> L[Learning / Consolidation]
    L --> M
    L --> P
    L --> WM
```

这张图是全书唯一的“总架构”。任何新技术都应能说明自己修改了哪一条边、哪一个状态或哪一个时间尺度。

---

# Figure 2　从任务意图到电机：Action 到底去了哪里

```mermaid
flowchart LR
    G[Goal / Language] --> Policy[Policy / VLA]
    Obs[RGB-D / State / Tactile] --> Policy
    Policy --> AR[Action Representation]
    AR -->|Delta Pose| TF[Frame Transform]
    TF --> IK[IK / Differential IK]
    AR -->|Joint Target| JC[Joint Controller]
    IK --> JC
    JC --> CMD[Position / Velocity / Torque Command]
    CMD --> BUS[CAN / EtherCAT / Driver]
    BUS --> MOTOR[Motor / Actuator]
    MOTOR --> BODY[Robot Dynamics]
    BODY --> WORLD[Physical World]
    WORLD --> Obs
```

核心提醒：论文里的 `action` 通常不是电机电流。Action space 只是整个控制链中的一个接口。

---

# Figure 3　坐标系与 SE(3) 数据流

```mermaid
flowchart LR
    W[World Frame] -->|T_world_base| B[Base Frame]
    B -->|T_base_camera| C[Camera Frame]
    B -->|FK q| E[End-Effector Frame]
    C -->|Back-project RGB-D| P[3D Point / Object Pose]
    P -->|T_world_camera| W
    W -->|Target Pose| E
```

机器人系统中的大量“模型错误”其实是 frame convention、左右乘、四元数顺序或时间戳错误。

---

# Figure 4　经典机器人控制的多时间尺度层级

```mermaid
flowchart TD
    Task[Task / Reasoning
~0.2-5 Hz] --> Skill[Skill / VLA / Planner
~1-50 Hz]
    Skill --> Motion[Motion Target / MPC / WBC
~20-200 Hz]
    Motion --> Servo[Joint / Torque Servo
~200-2000+ Hz]
    Servo --> Plant[Robot + Contact]
    Plant --> Est[State Estimation]
    Est --> Servo
    Est --> Motion
    Est --> Skill
    Plant --> Sensor[Vision / Tactile / Proprioception]
    Sensor --> Task
```

具体频率因硬件而异；图中数字表示典型数量级，而非标准值。关键是：**具身智能天然是 multi-rate system。**

---

# Figure 5　Robot Learning 数据闭环

```mermaid
flowchart TD
    Human[Human Demonstration] --> Data[Robot Dataset]
    Sim[Simulation / Synthetic Data] --> Data
    Real[Real Robot Experience] --> Data
    Video[Human / Internet Video] --> Pre[Representation / Prior]
    Data --> Train[BC / RL / Generative Policy Training]
    Pre --> Train
    Train --> Policy[Policy]
    Policy --> Deploy[Deployment]
    Deploy --> Outcome[Success / Failure / Intervention]
    Outcome --> Mine[Failure Mining / Curation]
    Mine --> Data
```

这张图把“大数据”从静态 dataset 改写成持续 data flywheel。

---

# Figure 6　BC → DAgger → RL → Experience Learning

```mermaid
flowchart LR
    D[Expert Dataset] --> BC[Behavior Cloning]
    BC --> Roll[Policy Rollout]
    Roll --> Shift[Covariate Shift / Failure]
    Shift --> DAgger[DAgger / Human Intervention]
    DAgger --> D
    Roll --> Reward[Outcome / Reward]
    Reward --> ORL[Offline / Online RL]
    ORL --> Improve[Policy Improvement]
    Improve --> Roll
```

它展示了 Robot Learning 的逻辑递进：从“模仿专家分布”逐渐走向“根据自己产生的状态和结果继续学习”。

---

# Figure 7　生成式动作模型的统一视图

```mermaid
flowchart TD
    C[Condition
Vision + Language + State] --> R[Regression]
    C --> AR[Autoregressive Tokens]
    C --> DIF[Diffusion]
    C --> FLOW[Flow Matching]
    R --> A[Action Chunk]
    AR --> A
    DIF --> A
    FLOW --> A
    A --> EX[Temporal Executor]
    EX --> WORLD[Robot / World]
    WORLD --> C
```

比较模型时必须固定 action horizon、control frequency、history、data 和 latency，否则“生成范式比较”不公平。

---

# Figure 8　现代 VLA 的共同结构

```mermaid
flowchart TD
    IMG[Images / Video] --> VE[Vision Encoder / VLM]
    LANG[Language] --> LM[Language Backbone]
    STATE[Proprioception] --> SE[State Encoder]
    EMB[Embodiment Descriptor] --> EE[Embodiment Encoder]
    VE --> FUSION[Multimodal Fusion]
    LM --> FUSION
    SE --> FUSION
    EE --> FUSION
    FUSION --> AE[Action Expert / Head]
    AE --> CHUNK[Action Chunk]
    CHUNK --> RT[RTC / Async Executor]
    RT --> CTRL[Low-Level Controller]
    CTRL --> ROBOT[Robot]
    ROBOT --> IMG
    ROBOT --> STATE
```

不同 VLA 的关键分歧主要发生在：representation 是否 joint-train、action generator 类型、embodiment conditioning、temporal execution 与 post-training。

---

# Figure 9　Reasoning、Memory 与 Policy 的分层

```mermaid
flowchart TD
    Goal[Long-Horizon Goal] --> Reason[Embodied Reasoning / Planner]
    Memory[(Long-Term Memory)] --> Reason
    Scene[Current Belief / Scene State] --> Reason
    Reason --> Sub[Subgoal / Skill]
    Sub --> Policy[Fast VLA / Skill Policy]
    Short[(Short-Term Sensorimotor Memory)] --> Policy
    Policy --> Robot[Robot]
    Robot --> Observe[Observation / Progress]
    Observe --> Short
    Observe --> Verify[Progress / Failure Monitor]
    Verify --> Reason
    Verify --> Memory
```

长任务不是“把 action chunk 拉长”，而是把不同时间尺度的记忆、计划、执行和验证闭环起来。

---

# Figure 10　World Model 的最小可用结构

```mermaid
flowchart LR
    O[Observation] --> E[Encoder]
    E --> Z[Latent State z_t]
    A[Candidate Action] --> F[Action-Conditioned Dynamics]
    Z --> F
    F --> ZF[Predicted Future z_t+1:t+H]
    ZF --> R[Reward / Goal / Constraint Evaluator]
    R --> SEARCH[Search / MPC / Policy Selection]
    SEARCH --> EXEC[Execute First Action]
    EXEC --> REAL[Real World]
    REAL --> O
```

真正的检验不是 future video 好不好看，而是 **counterfactual prediction 是否改善真实 action selection**。

---

# Figure 11　主动感知：看哪里也是动作

```mermaid
flowchart TD
    Belief[Current Belief + Uncertainty] --> Value[Expected Information Gain]
    Task[Task Relevance] --> Value
    Cost[Motion / Time / Risk Cost] --> Value
    Value --> VG[View / Touch Goal]
    VG --> Planner[Embodiment-Specific Motion Planner]
    Planner --> Body[Camera / Head / Base / Hand]
    Body --> NewObs[New Observation]
    NewObs --> Belief
```

这一结构把高层“应该获取什么信息”与具体机器人“怎样移动去获取”分开，可自然支持 embodiment-agnostic sensing goal。

---

# Figure 12　双臂 / 灵巧操作的协调关系

```mermaid
flowchart TD
    Goal[Object-Centric Goal] --> Coord[Coordination Representation]
    Coord --> L[Left Arm / Hand Target]
    Coord --> R[Right Arm / Hand Target]
    L --> Obj[Shared Object / Contact Graph]
    R --> Obj
    Obj --> Force[Relative Pose / Internal Force / Slip]
    Force --> Coord
    TacL[Tactile L] --> Force
    TacR[Tactile R] --> Force
```

双臂的核心不是把 action vector 拼成两倍，而是建模共同对象、相对约束与 internal force。

---

# Figure 13　Whole-Body Humanoid：Feet-to-Fingertips

```mermaid
flowchart TD
    Goal[Task Goal] --> High[Reasoning / Whole-Body Policy]
    Per[Vision + Proprioception + Tactile] --> High
    High --> Loc[Locomotion Intent]
    High --> Manip[Manipulation Intent]
    Loc --> WBC[Whole-Body Controller / Motion Prior]
    Manip --> WBC
    WBC --> Legs[Legs / Feet Contacts]
    WBC --> Torso[Torso / Balance]
    WBC --> Arms[Arms / Hands]
    Legs --> Dyn[Floating-Base Dynamics]
    Torso --> Dyn
    Arms --> Dyn
    Dyn --> Per
```

“全身 VLA”必须面对一个事实：手臂动作会改变 balance，腿部动作会改变 camera 和 arm workspace。

---

# Figure 14　Cross-Embodiment：从任务规律到不同身体

```mermaid
flowchart TD
    Task[Task / Desired Physical Effect] --> Core[Embodiment-Agnostic Skill / Mechanism]
    MorphA[Robot A Morphology] --> DecA[Embodiment Decoder A]
    MorphB[Robot B Morphology] --> DecB[Embodiment Decoder B]
    MorphC[Unseen Robot C] --> DecC[Adapt / Retarget]
    Core --> DecA
    Core --> DecB
    Core --> DecC
    DecA --> ActA[Action A]
    DecB --> ActB[Action B]
    DecC --> ActC[Action C]
```

真正 cross-embodiment 的核心是共享 **effect / mechanism**，而不是把不同机器人的 joint vectors padding 到相同长度。

---

# Figure 15　Continual / Developmental / Self-Evolving Loop

```mermaid
flowchart TD
    Env[Physical Environment] --> Exp[Experience]
    Exp --> Eval[Outcome / Surprise / Failure]
    Eval --> Mem[Episodic Memory]
    Mem --> Consol[Consolidation]
    Consol --> Sem[Semantic / Mechanism Memory]
    Consol --> Policy[Policy Update]
    Consol --> World[World Model Update]
    Consol --> Struct[Structural Change]
    Policy --> Act[Action / Exploration]
    World --> Act
    Sem --> Act
    Struct --> Policy
    Act --> Env
    Safety[Persistent Safety Invariants] --> Act
    Safety --> Struct
```

这张图刻意把 parameter update、memory formation 与 architecture change 分开：发展型智能不能被简化为 continual fine-tuning。

---

# Figure 16　从 Paper Claim 到可证伪科学结论

```mermaid
flowchart LR
    Claim[Paper Claim] --> Hyp[Specific Hypothesis]
    Hyp --> Mechanism[Intermediate Mechanism]
    Mechanism --> Test[Minimal Controlled Experiment]
    Test --> Pos[Positive Control]
    Test --> Neg[Negative Control]
    Pos --> Result[Metrics + Confidence]
    Neg --> Result
    Result -->|supports| Scale[Scale Up]
    Result -->|falsifies| Revise[Revise Hypothesis]
    Revise --> Hyp
```

这是全书研究方法的核心：算力放在已经通过最小可证伪实验的问题上，而不是代替实验设计。

---

# Figure 17　全书知识依赖图

```mermaid
flowchart TD
    Math[Math / Probability / Optimization] --> Geo[Geometry / Kinematics]
    Math --> Dyn[Dynamics / Control]
    Body[Body / Hardware] --> Geo
    Body --> Dyn
    Geo --> Per[Perception / State]
    Dyn --> Plan[Planning / Control]
    Per --> Learn[Robot Learning]
    Plan --> Learn
    Learn --> VLA[VLA / Foundation Policy]
    VLA --> Reason[Reasoning / Memory]
    VLA --> WM[World Models]
    Reason --> Cap[Manipulation / Navigation / Humanoid]
    WM --> Cap
    Cap --> Cross[Cross-Embodiment / Continual]
    Cross --> Sys[Simulation / Data / Deployment]
    Sys --> Eval[Evaluation / Safety]
    Eval --> Research[Mechanism Research / New Architectures]
```

建议第一次学习时沿这张图顺序推进；做科研时则从某个 failure 反向追溯它依赖的基础层。

---

# 图示维护原则

1. **模型图必须同时画 action 执行端。** 不能只画到 policy output。
2. **坐标图必须写 frame。** `world/base/camera/ee/object` 不能省。
3. **时间图必须写频率或相对尺度。** 尤其 VLA、tactile、controller。
4. **表示图必须写 shape / object semantics。** 不允许只画“Encoder → Feature”。
5. **World Model 图必须含 action conditioning。** 否则只是视频预测。
6. **Reasoning 图必须含 execution feedback。** 否则只是 open-loop planner。
7. **Continual learning 图必须区分 memory、parameter、structure。**
8. 前沿模型的品牌架构图放入对应 Atlas；主教材优先保留能长期成立的机制图。