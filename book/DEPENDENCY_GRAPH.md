# Knowledge Dependency Graph

> The table of contents is linear because books are read linearly. The knowledge itself is not. This file exposes the prerequisite graph so readers can enter from different backgrounds without losing the dependency structure.

# 1. Global graph

```mermaid
flowchart TD
    A0[Part 0 Embodied Intelligence]
    A1[Part 1 History]

    M2[Part 2 Linear Algebra / Calculus]
    M3[Part 3 Probability / Information]
    M4[Part 4 Optimization / Dynamics]
    M5[Part 5 Geometry / Graphs / Causality]

    R6[Part 6 Robot Body]
    R7[Part 7 Rigid-Body Geometry]
    R8[Part 8 Kinematics]
    R9[Part 9 Dynamics / Contact]
    R10[Part 10 Control]
    R11[Part 11 Planning]

    P12[Part 12 Sensors]
    P13[Part 13 2D Vision]
    P14[Part 14 3D/4D World]
    P15[Part 15 State Estimation]
    P16[Part 16 Tactile]
    P17[Part 17 Active Perception]

    L18[Part 18 ML for Robots]
    L19[Part 19 Imitation]
    L20[Part 20 RL]
    L21[Part 21 Generative Actions]

    F22[Part 22 VLM / Grounding]
    F23[Part 23 VLA Formation]
    F24[Part 24 VLA 2024-2026]
    F25[Part 25 VLA Internals]
    F26[Part 26 Data / Cross-Embodiment]

    W27[Part 27 Reasoning]
    W28[Part 28 Memory]
    W29[Part 29 Experience Learning]
    W30[Part 30 World Models]
    W31[Part 31 Generative Worlds]

    C32[Part 32 Manipulation]
    C33[Part 33 Bimanual / Dexterity]
    C34[Part 34 Navigation]
    C35[Part 35 Humanoid]
    C36[Part 36 HRI / Multi-Robot]

    D37[Part 37 Cross-Embodiment]
    D38[Part 38 Continual / Developmental]
    D39[Part 39 Self-Evolving]

    S40[Part 40 Simulation]
    S41[Part 41 Sim2Real]
    S42[Part 42 Data Engineering]
    S43[Part 43 Deployment]
    S44[Part 44 Evaluation]
    S45[Part 45 Safety]

    X46[Part 46 Research Method]
    X47[Part 47 Transformer Limits]
    X48[Part 48 Mathematical EI]
    X49[Part 49 Open Frontiers]
    X50[Part 50 Independent Researcher]

    A0 --> M2
    A0 --> M3
    A0 --> R6
    A1 --> F23

    M2 --> R7
    M2 --> R8
    M2 --> R10
    M3 --> P15
    M3 --> P17
    M3 --> L20
    M4 --> R9
    M4 --> R10
    M4 --> R11
    M4 --> L20
    M4 --> L21
    M5 --> R7
    M5 --> P14
    M5 --> X48

    R6 --> R8
    R6 --> R9
    R7 --> R8
    R8 --> R9
    R8 --> R10
    R9 --> R10
    R10 --> R11

    R7 --> P12
    P12 --> P13
    P12 --> P15
    P12 --> P16
    P13 --> P14
    P14 --> P15
    P15 --> P17
    P16 --> P17

    M2 --> L18
    M3 --> L18
    L18 --> L19
    L18 --> L20
    L18 --> L21
    L19 --> F23
    L20 --> W29
    L21 --> F24

    P13 --> F22
    P14 --> F22
    F22 --> F23
    F23 --> F24
    F23 --> F25
    F24 --> F25
    F25 --> F26

    F25 --> W27
    F25 --> W28
    L20 --> W29
    W28 --> W29
    P15 --> W30
    L18 --> W30
    W30 --> W31

    R8 --> C32
    R9 --> C32
    R10 --> C32
    P14 --> C32
    C32 --> C33
    P16 --> C33

    P15 --> C34
    R11 --> C34

    R9 --> C35
    R10 --> C35
    L20 --> C35
    C32 --> C35

    W27 --> C36
    W28 --> C36

    F26 --> D37
    C35 --> D37
    W29 --> D38
    D37 --> D38
    D38 --> D39

    R9 --> S40
    R10 --> S40
    S40 --> S41
    F26 --> S42
    S42 --> S43
    R10 --> S43
    S43 --> S44
    S44 --> S45

    X46 --> X49
    X47 --> X49
    X48 --> X49
    X49 --> X50

    S44 --> X46
    W30 --> X47
    D39 --> X49
```

---

# 2. Classical robotics dependency chain

```mermaid
flowchart LR
    LA[Linear Algebra] --> SE3[SO(3) / SE(3)]
    SE3 --> FK[Forward Kinematics]
    FK --> J[Jacobian]
    J --> IK[Inverse Kinematics]
    IK --> CTRL[Task / Joint Control]
    DYN[Dynamics] --> CTRL
    CONTACT[Contact] --> CTRL
    CTRL --> PLAN[Motion / TAMP]
```

Minimal prerequisite order:

```text
Part 2 → 7 → 8 → 9 → 10 → 11
```

If you skip Part 7, later pose/action conventions become fragile. If you skip Part 9, learned control/contact claims are hard to evaluate physically.

---

# 3. Perception and state dependency chain

```mermaid
flowchart LR
    SENSOR[Sensors / Calibration / Time]
    V2[2D Vision]
    V3[3D/4D Representation]
    EST[State Estimation]
    TOUCH[Tactile]
    ACTIVE[Active Perception]

    SENSOR --> V2
    SENSOR --> EST
    V2 --> V3
    V3 --> EST
    TOUCH --> EST
    EST --> ACTIVE
    TOUCH --> ACTIVE
```

Core principle:

> active perception should consume an explicit uncertainty/belief estimate; otherwise “move the camera around” is not yet an information-seeking policy.

---

# 4. Robot-learning dependency chain

```mermaid
flowchart TD
    ML[Part 18 ML for Robots]
    IL[Part 19 Imitation]
    RL[Part 20 RL]
    GEN[Part 21 Generative Actions]
    VLA[Parts 23-25 VLA]
    EXP[Part 29 Experience Learning]

    ML --> IL
    ML --> RL
    ML --> GEN
    IL --> VLA
    GEN --> VLA
    RL --> EXP
    VLA --> EXP
```

Important asymmetry:

- imitation gives strong priors but weak recovery;
- RL supplies interaction-based improvement but is expensive/risky;
- generative action models handle multimodality but do not solve state uncertainty by themselves.

---

# 5. VLA dependency chain

```mermaid
flowchart TD
    VLM[VLM / Grounding]
    IL[Imitation Learning]
    GEN[Action Generation]
    DATA[Robot Data Mixtures]
    VLA1[VLA Formation]
    VLA2[VLA Second Stage]
    INT[VLA Internals]
    REASON[Reasoning]
    MEM[Memory]
    EXP[Experience Learning]

    VLM --> VLA1
    IL --> VLA1
    GEN --> VLA2
    DATA --> VLA1
    VLA1 --> VLA2
    VLA1 --> INT
    VLA2 --> INT
    INT --> REASON
    INT --> MEM
    REASON --> EXP
    MEM --> EXP
```

A student should not enter Part 24 before understanding:

- Part 19: what distribution a demonstration defines;
- Part 21: how actions are generated and executed;
- Part 22: what language/vision grounding contributes;
- Part 23: the first VLA architecture family.

---

# 6. World-model dependency chain

```mermaid
flowchart LR
    STATE[State / Representation] --> DYN[Learned Dynamics]
    ACTION[Action] --> DYN
    DYN --> FUTURE[Predicted Future]
    FUTURE --> COST[Evaluator / Cost]
    COST --> PLAN[Planning / Search]
    PLAN --> EXEC[Execute first action]
    EXEC --> OBS[Observe again]
    OBS --> STATE
```

Required prerequisites:

```text
Part 3 uncertainty
+ Part 4 dynamics/decision
+ Part 15 state estimation
+ Part 21 action representation
→ Part 30 world models
```

This makes it explicit why a video generator alone is not automatically a planning world model.

---

# 7. Humanoid dependency chain

```mermaid
flowchart TD
    BODY[Robot Body / Actuation]
    DYN[Whole-Body Dynamics]
    CTRL[WBC / HQP]
    RL[Locomotion RL / Motion Prior]
    VISION[Perception / State Estimation]
    MANIP[Manipulation]
    VLA[Foundation Policy]
    HUM[Whole-Body Humanoid Intelligence]

    BODY --> DYN
    DYN --> CTRL
    RL --> HUM
    CTRL --> HUM
    VISION --> HUM
    MANIP --> HUM
    VLA --> HUM
```

Humanoid is therefore a convergence chapter rather than an isolated model family.

---

# 8. Cross-embodiment and continual learning

```mermaid
flowchart LR
    DESC[Embodiment Descriptor]
    SHARED[Shared Representation / Skill Space]
    ADAPT[Calibration / Adapter / Few-shot Adaptation]
    TRANSFER[Cross-Robot Transfer]
    MEMORY[Continual Memory]
    PLASTIC[Structural Plasticity]
    DEVELOP[Developmental Agent]

    DESC --> SHARED
    SHARED --> ADAPT
    ADAPT --> TRANSFER
    TRANSFER --> MEMORY
    MEMORY --> PLASTIC
    PLASTIC --> DEVELOP
```

Key distinction:

> cross-embodiment asks whether capability can move across bodies; continual learning asks whether capability can accumulate across time. A developmental agent eventually needs both.

---

# 9. Infrastructure dependency chain

```mermaid
flowchart LR
    SIM[Simulation] --> S2R[Sim-to-Real]
    DATA[Data Engineering] --> TRAIN[Training]
    TRAIN --> DEPLOY[Deployment]
    S2R --> DEPLOY
    DEPLOY --> EVAL[Evaluation]
    EVAL --> SAFE[Safety / Reliability]
    SAFE --> DATA
```

This is a closed engineering/scientific loop: deployment produces new failures and data, which should return into training and evaluation.

---

# 10. Research methodology dependency chain

```mermaid
flowchart TD
    QUESTION[Question]
    HYP[Hypothesis]
    MECH[Mechanism]
    MIN[Minimal Experiment]
    NEG[Negative Control]
    FAIL[Failure Taxonomy]
    SCALE[Scale-up]
    THEORY[Generalization / Theory]

    QUESTION --> HYP
    HYP --> MECH
    MECH --> MIN
    MIN --> NEG
    NEG --> FAIL
    FAIL --> SCALE
    SCALE --> THEORY
```

This graph should be applied to every capstone and research project in the repository.

---

# 11. Entry points by background

## Deep-learning background

Start:

```text
Part 0 → 6–12 → 15 → 18–26 → 30 → 43–46
```

Then fill math gaps from Parts 2–5 as required.

## Robotics/control background

Start:

```text
Part 0 → 18–26 → 27–31 → 37–39 → 46–49
```

## Computer-vision background

Start:

```text
Part 0 → 6–12 → 13–17 → 18–26 → 30–31
```

## Foundation-model background

Do **not** start only at Part 23. Minimum prerequisite bridge:

```text
Part 6 → 7 → 8 → 9 → 10 → 12 → 15 → 19 → 21 → 22 → 23
```

---

# 12. Dependency maintenance rule

When adding a new chapter or major topic, update this graph with:

1. prerequisites;
2. outputs consumed downstream;
3. whether the dependency is mathematical, physical, algorithmic or engineering;
4. whether the new node is truly fundamental or only a case study.

A book chapter that has no clear incoming or outgoing knowledge dependency should be treated with suspicion: it may be a temporary trend rather than part of the durable curriculum.
