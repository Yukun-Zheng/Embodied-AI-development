# Volume VII　操作、导航、灵巧与人形

> 到这一卷，我们不再按模型架构划分问题，而按**机器人真正需要完成的能力**来组织：操作物体、协调双手、在空间中移动、保持平衡、全身协同，以及与人和其他机器人共同工作。相同的 VLA / RL / world model，在不同能力域面对的物理约束完全不同。

---

# Part 32　机器人操作：从抓取到长时程任务

## 32.1 Manipulation 的本质

操作不是“机械臂运动到一个点”，而是通过接触主动改变环境状态：

\[
s_{t+1}=F(s_t,a_t,c_t),
\]

其中 \(c_t\) 是接触模式。真正难点往往不在 free-space motion，而在 contact mode 变化：未接触 → 接触 → 滑动 → 抓住 → 搬运 → 放置。

## 32.2 Reach / Push / Pull

Reach 主要受 kinematics、collision 和 tracking 约束；push / pull 则开始依赖 friction、contact point 和 object dynamics。

推一个物体时，动作效果不仅由末端位姿决定：

\[
\Delta s_{obj}=f(p_{contact},n_{contact},v_{ee},\mu,m,I,\text{support}).
\]

这类任务是检验“模型到底懂不懂物理”的最小试金石。

## 32.3 Pick-and-Place

典型闭环：

```text
object detection / pose
        ↓
grasp proposal
        ↓
pre-grasp motion
        ↓
contact + close gripper
        ↓
lift verification
        ↓
transport
        ↓
placement + release verification
```

每一步都可能失败。只报告最终 success 会掩盖是 perception、planning、grasp、slip 还是 placement 出错。

## 32.4 Grasp Planning

抓取 \(g\) 可表示为末端 pose + gripper configuration：

\[
g=(T_{ee},q_g).
\]

经典方法按 force closure、collision、reachability 打分；学习方法从 RGB-D/point cloud 预测 grasp quality：

\[
Q(g\mid o).
\]

真正可执行 grasp score 应至少乘上几何可达性：

\[
Q_{exec}(g)=Q_{grasp}(g)\,P(\mathrm{IK})\,P(\mathrm{collision\ free}).
\]

## 32.5 Contact-Rich Manipulation

插孔、装配、旋拧、开关等任务需要利用接触，而不是避免接触。状态常部分不可观测，仅从 RGB 很难判断毫米级偏差。

常见策略：

- impedance / force control；
- compliant search；
- tactile / F/T residual；
- learned contact policy；
- world model + contact event prediction。

## 32.6 Tool Use

工具改变身体的有效几何与动力学。拿起锤子后，末端有效操作点从手变成锤头：

\[
{}^WT_{tool}={}^WT_{hand}\,{}^{hand}T_{tool}.
\]

真正 tool-use intelligence 需要估计工具 functional part、grasp、effect 和安全约束，而不是只识别“这是锤子”。

## 32.7 Articulated Objects

抽屉、门、剪刀等具有内部关节。可以将物体写成小型 kinematic tree，并估计 articulation axis / limit：

\[
q_{obj}\in\mathbb R^k.
\]

如果模型知道“抽屉只能沿某轴平移”，它就比只记视觉轨迹更容易跨不同柜子泛化。

## 32.8 Deformable Objects

cloth / rope / cable 状态维数远高于 rigid body。局部动作可引起全局形变，且视觉自遮挡严重。

常见表示：keypoints、dense point cloud、mesh、curve centerline、latent state。对 cloth folding，拓扑关系和接触顺序往往比单帧像素更关键。

## 32.9 Liquids / Granular / Food

液体、颗粒和食物处理进一步打破刚体假设。很多“家庭机器人”长期能力最终必然面对 pouring、scooping、cutting、mixing 等连续材料过程。

这类任务要求感知材料状态、速度/力控制和 outcome estimation；目前仍是通用 VLA 的薄弱区。

## 32.10 Mobile Manipulation

移动操作将 base 与 arm 合并：

\[
q=[q_{base},q_{arm},q_{gripper}].
\]

base 可以扩大 reachability，但也引入 navigation uncertainty 和 whole-body collision。一个高层 target 可能有多个 base–arm 分解，因此需要 joint optimization 或 hierarchical planning。

## 32.11 Long-Horizon Manipulation

长任务失败率具有乘法效应。若每阶段成功率 \(p_i\)：

\[
P_{task}=\prod_i p_i.
\]

因此长任务重点不是把单 skill 从 90% 提到 91%，而是建立：progress tracking、failure detection、recovery、memory、replanning。

## 32.12 Open-World Household Manipulation

家庭环境的困难来自开放集合：物品位置变化、对象从未见过、柜门状态变化、人可能中途干预、空间狭窄、任务语言含糊。真正 open-world 评测应在**新家庭**而不是训练厨房随机换颜色。

## 32.13 Industrial Manipulation

工业场景通常更结构化，但要求更高 reliability、cycle time、精度和 certification。foundation policy 要进入工业，不只看平均 success，还要回答：

- 99.9% 以上任务如何达到？
- failure 是否可检测？
- recovery 多快？
- 轨迹是否满足速度/力限制？
- 系统如何验证和回滚？

## 32.14 Manipulation Failure Taxonomy

建议统一记录：

1. perception failure；
2. bad grasp proposal；
3. IK / collision infeasible；
4. approach error；
5. contact misalignment；
6. insufficient/excessive force；
7. slip/drop；
8. object state estimation error；
9. task progress / reasoning error；
10. latency / stale action；
11. controller/hardware fault。

Failure taxonomy 是建立 data flywheel 的前提。

---

# Part 33　双臂、灵巧手与触觉智能

## 33.1 为什么双臂不是两个单臂

两个独立 policy：

\[
a_L=\pi_L(o),\qquad a_R=\pi_R(o)
\]

无法自然表达两臂相互约束。双臂任务真正的 state 常包含：

\[
T_L,T_R,{}^LT_R,F_L,F_R,\text{shared object state}.
\]

尤其共同持物时，两臂通过对象形成闭链，动作强耦合。

## 33.2 Relative Pose / Coordinated Frame

很多双臂任务应在相对坐标表达：

\[
{}^LT_R=({}^WT_L)^{-1}{}^WT_R.
\]

如果目标是保持双手间距离/朝向，relative frame 比各自在 world frame 跟踪 target 更稳健。

## 33.3 Symmetric / Asymmetric Coordination

- symmetric：双手共同抬箱子；
- asymmetric：一手固定、一手旋拧；
- complementary：一手拉开袋口、一手放物；
- sequential：handover。

不同模式需要不同 coordination variable，不能用“bimanual action dimension 更大”概括。

## 33.4 Handover

handover 至少有四阶段：approach → dual grasp/contact → load transfer → release。关键是 transfer condition：接收手是否真正承重？

可用 F/T 或 tactile 判断：

\[
F_{receiver}>F_{threshold}
\]

再释放 giver，比纯视觉 timer 更可靠。

## 33.5 Cooperative Manipulation 与 Internal Force

双手共同抓刚体时，可以产生不改变物体净 wrench 的 internal force。控制时既要满足 object motion，又要避免 internal force 过大损坏物体。

概念上：

\[
\tau=J^T_{obj}W_{task}+N\,f_{internal}.
\]

## 33.6 Collision 与 Safety

双臂系统多了一类 self-collision：两臂、手、工具、共享对象之间。learned policy 若没有显式 collision awareness，很容易在训练分布外互撞。

可加：distance field、collision-aware IK、safety QP、runtime shield。

## 33.7 Dexterous Hand Kinematics

灵巧手可能 15–30+ DOF，但 actuator 数量、tendon coupling 和 joint limits 使实际可控空间远小于独立关节笛卡尔积。

常用 synergy：

\[
q_{hand}\approx q_0+Sy,
\]

其中低维 \(y\) 控制常见 hand posture。

## 33.8 Underactuation

欠驱动手利用机械耦合自动适应物体形状。它说明“更多独立 DOF = 更智能”并不成立。机械设计可以把部分 grasp adaptation 从控制问题转移给 morphology。

## 33.9 In-Hand Manipulation

目标是在不放开物体的情况下改变 object pose。需要 fingers rolling/sliding、接触切换和内部力管理。

状态可以写：

\[
s=(q_{hand},T_{object},C,F).
\]

其中 \(C\) 是 contact configuration。

## 33.10 Tactile Dexterity

灵巧手视觉自遮挡严重，触觉成为关键：

- object slip；
- contact patch；
- normal/shear force；
- rolling direction；
- incipient failure。

高频 tactile residual policy 可以在慢速视觉/VLA 之外形成类似“反射弧”的回路。

## 33.11 Human Motion Retargeting

人手 demonstration 到 robot hand 不是逐关节复制。通常优化 task-space keypoints / contact：

\[
\min_{q_r}\sum_i\|p_i^{robot}(q_r)-\hat p_i^{human}\|^2+\lambda R(q_r)
\]

subject to robot joint limits / collision。

## 33.12 Dexterous RL

高维 hand RL 常依赖：大量并行 simulation、privileged state、curriculum、domain randomization、motion prior。训练成功后再通过 vision/tactile student 蒸馏到可部署 observation。

## 33.13 Bimanual / Dexterous VLA

当 VLA 输出双臂或手指动作时，真正挑战不是 output dimension 本身，而是：

- temporal synchrony；
- relative constraint；
- contact phase；
- force/tactile feedback；
- higher action bandwidth。

因此通用 VLA 往往仍需要更快的 low-level dexterous controller。

## 33.14 离人类灵巧性还差什么

人类优势来自感知、身体和学习共同体：高密度触觉、本体感觉、顺应肌腱、丰富先验、长期自监督练习、快速反射。单纯把 Transformer 参数增大，无法直接补齐这些缺口。

---

# Part 34　移动机器人、导航与 Embodied Navigation

## 34.1 Mobile Base

Differential drive：

\[
v=\frac r2(\omega_R+\omega_L),\qquad
\dot\theta=\frac rL(\omega_R-\omega_L).
\]

它有 nonholonomic constraint，不能瞬间横移。Omnidirectional base 则可在平面上更自由运动。

## 34.2 Localization 与 Mapping

导航系统通常维护 robot pose：

\[
x=(x,y,\theta)
\]

并用 map 表示 obstacle / semantic landmark。SLAM 提供 map 与 trajectory；学习方法可直接从视觉 latent 导航，但仍要解决定位漂移和障碍。

## 34.3 Global / Local Navigation

传统 Nav stack：

```text
map + goal
   ↓
global planner
   ↓
reference path
   ↓
local planner / obstacle avoidance
   ↓
velocity command
```

foundation model 更适合提供 semantic goal / high-level route，而底层 collision avoidance 仍可由成熟 local controller 保证。

## 34.4 Visual Navigation

输入 RGB/RGB-D，输出 waypoint/velocity。关键任务：PointNav、ObjectNav、ImageNav、InstanceNav。训练常在 Habitat / Gibson / HM3D 等 simulator，真机则受 camera calibration、motion blur、dynamic person 等影响。

## 34.5 Vision-Language Navigation

VLN 输入自然语言路线，如“穿过客厅，在沙发旁右转”。需要 language grounding、map/memory、spatial reasoning、progress estimation。

与 manipulation VLA 不同，VLN action horizon 长、场景尺度大，memory 更重要。

## 34.6 Semantic Map

地图不只存 occupancy，还可存 object/category/affordance：

\[
M(x,y)=[p_{occ},\text{semantic},\text{uncertainty}].
\]

语言任务“去厨房拿杯子”可先在 semantic map 中找到 kitchen / cup candidate，再导航。

## 34.7 Topological Memory

大环境不一定需要厘米级 dense map，可维护 place graph：房间/关键视点是 node，可通行关系为 edge。Topological memory 更适合长距离和多次访问。

## 34.8 Active Exploration

未知环境中需要同时探索与任务：frontier exploration 最大化未知区域覆盖；task-driven exploration 则优先寻找目标类别或信息价值高区域。

## 34.9 Social Navigation

有人环境中“几何不碰撞”还不够。机器人需遵守个人空间、让行、走廊方向、人群流动等社会规范。

可将 cost 写为：

\[
J=J_{goal}+\lambda_cJ_{collision}+\lambda_sJ_{social}+\lambda_eJ_{efficiency}.
\]

## 34.10 Mobile Manipulation

导航终点并非一个点，而是**可操作 base pose**。机器人应该选使后续 manipulation 可达、视野好、碰撞余量大的站位：

\[
x_{base}^*=\arg\max_x P(\text{task success}\mid x).
\]

因此 navigation 与 manipulation 最终应联合规划。

## 34.11 Embodied Question Answering / Exploration

如果机器人被问“办公室里有几把椅子”，它必须移动获取证据。此类任务把 language reasoning 与 active perception 统一起来，是“具身”区别于 static VQA 的典型案例。

## 34.12 Field Robots / Drone / Autonomous Vehicle

虽然本书重点是 manipulation/humanoid，但无人机、无人车、野外机器人共享同一闭环框架：partial observability、dynamics、planning、safety、sim2real。Embodied AI 的数学骨架不绑定 humanoid。

---

# Part 35　Legged Locomotion、Humanoid 与 Whole-Body Intelligence

## 35.1 Legged State / Action

典型 state：

\[
s=[R_{base},\omega_{base},v_{base},q,\dot q,\text{contact},command].
\]

policy 常输出 joint target / torque，底层 PD/servo 执行。

## 35.2 Gait

步态描述脚的接触时序。四足常见 walk/trot/bound；双足核心是左右脚交替支撑。学习策略可能不显式编码 gait，但训练 curriculum 和 reward 会塑造接触模式。

## 35.3 Balance

平衡本质是调节 ground reaction force 和动量，使系统状态保持在可恢复区域。静态“重心投影在支撑面内”只是最简单情形；动态平衡需要考虑动量。

## 35.4 ZMP / Capture Point / Centroidal Dynamics

Centroidal momentum：

\[
h=A_G(q)\dot q.
\]

whole-body planning 可先规划 COM / centroidal momentum / contact force，再求全身关节轨迹。

Capture Point 在简化 inverted pendulum 下给出落脚点直觉：机器人若扰动太大，必须迈步才能恢复。

## 35.5 Quadruped RL

现代四足 locomotion 成熟 recipe：

1. thousands parallel envs；
2. proprioceptive policy；
3. privileged critic；
4. domain randomization；
5. terrain curriculum；
6. system identification；
7. low-latency deployment。

它是 simulation-to-real 最成功的 robot learning 范例之一。

## 35.6 Biped / Humanoid Locomotion

人形的难点是 floating base、高维、窄支撑面和碰撞。动作也必须兼顾未来 manipulation：一个“走得最稳”的姿态可能让双手不可用。

## 35.7 Motion Imitation

从 mocap / video retarget human motion，训练 tracking policy：

\[
r= w_q r_q+w_p r_p+w_v r_v+w_c r_{contact}.
\]

AMP / adversarial motion prior、diffusion motion prior 等进一步让动作更自然、更多样。

## 35.8 Whole-Body Manipulation

人形搬箱子时，不能把 legs 当固定底座。手部 wrench 会影响平衡，base movement 可扩大 reach。统一任务应同时规划：foot contacts、COM、torso、hands。

## 35.9 Locomotion + Manipulation

可采用：

- hierarchical：locomotion controller + arm policy；
- whole-body controller with learned reference；
- unified RL policy；
- whole-body VLA + low-level WBC；
- skill mixture / mode switching。

真正 general humanoid 最终必须平滑跨越这些 mode，而非人为按“走路/操作”切割。

## 35.10 Unified Action Space

whole-body action 可直接是所有关节 target：

\[
a\in\mathbb R^{n_{body}}.
\]

也可拆成高层 task-space command：

\[
a=[v_{base},T_{Lhand},T_{Rhand},g_L,g_R,\text{posture}].
\]

前者统一但学习难；后者利用 WBC/IK inductive bias。选择取决于数据与控制目标。

## 35.11 Feet-to-Fingertips Control

截至 2026，frontier 已明确向“从脚到底手指”的 whole-body foundation policy 演进：GR00T N1.6 加入 G1 loco-manipulation，Gemini Robotics 2 强调 full-body humanoid + dexterity，Figure Helix 将 torso/head/wrist/finger 纳入同一 upper-body policy。

研究重点从 tabletop success 变成：

\[
\text{mobility}+\text{balance}+\text{manipulation}+\text{reasoning}+\text{safety}.
\]

## 35.12 Fall Detection / Recovery

通用 humanoid 不能假设“永不摔倒”。系统需：

1. 检测不可恢复状态；
2. 采取 protective fall；
3. 判断环境安全；
4. self-righting / stand-up；
5. 恢复任务 memory。

这类 recovery 能力比单次 benchmark 平均 reward 更接近真实部署。

## 35.13 Energy、Speed、Thermal

人形必须受 battery、motor temperature、torque-speed curve 约束。真实评价除 success 外还应报告：

\[
E=\int |\tau^T\dot q|dt,
\]

cycle time、peak torque、thermal margin。

## 35.14 Humanoid 的现实瓶颈

主要瓶颈不是一个单一算法：

- 高质量真实数据昂贵；
- hand/tactile 仍弱；
- actuator reliability；
- battery/endurance；
- fall safety；
- whole-body data distribution；
- long-horizon reasoning/recovery；
- low-latency onboard compute；
- maintenance cost。

“长得像人”不自动意味着拥有人的通用性。

---

# Part 36　Human–Robot Interaction 与 Multi-Robot Intelligence

## 36.1 Human-in-the-Loop Robotics

人在系统中可以扮演：teacher、operator、supervisor、collaborator、safety fallback。不同角色要求不同 interface 与权限。

## 36.2 Shared Autonomy

用户输入 \(u_h\)，机器人自主策略 \(u_r\)，共享控制可写：

\[
u=\alpha u_h+(1-\alpha)u_r,
\]

但实际 \(\alpha\) 应根据 confidence、task phase、safety 动态变化，而不是固定加权。

## 36.3 Interactive Correction

自然语言“再往左一点”“不要抓杯口”可作为 dense guidance。π0.7 所强调的 steerability 就把 language coaching 从任务描述扩展成行为调节接口。

要验证 correction 真正有效，应比较：有/无 correction、随机 correction、冲突 correction。

## 36.4 Human Intent 与 Predictability

协作机器人不仅要预测人下一步，还要让**自己的行为可被人预测**。最优机器人路径未必是最好的交互路径；突兀高效动作可能降低人类信任与安全。

## 36.5 Physical Collaboration

共同抬物体、递工具时，人和机器人构成耦合动力系统。需估计 human-applied wrench / intent，并通过 compliance 避免抢力。

## 36.6 Multi-Robot State

多机器人系统：

\[
s=(s_1,\ldots,s_N,s_{env}),
\qquad
 a=(a_1,\ldots,a_N).
\]

困难来自 joint action space 指数增长、通信限制和 partial observability。

## 36.7 Communication

通信可以是显式 message \(m_i\)，也可以通过行为隐式传递。带宽、延迟、丢包必须进入算法假设：

\[
m_i(t-\Delta)\ne m_i(t).
\]

集中式“所有 agent 实时共享完整 observation”往往不符合真机。

## 36.8 Task Allocation

多个任务 \(T_j\) 分给 robot \(R_i\)，可用 assignment：

\[
\min_x \sum_{ij}c_{ij}x_{ij}
\]

subject to capacity / precedence / availability。LLM 可做语义 decomposition，但资源约束和路径冲突仍需显式优化。

## 36.9 Coordination

多机器人协调包括：collision-free trajectory、shared object manipulation、handover、空间资源互斥、共同探索。

很多问题可视为 constraint graph：节点是 agents/tasks，边表示耦合。

## 36.10 Centralized Training / Decentralized Execution

训练时可让 critic 看到全局 state，执行时每个 agent 只用本地 observation：

\[
\pi_i(a_i\mid o_i,m_i),
\qquad
Q(s,a_1,\ldots,a_N).
\]

这是 MARL 常见结构。

## 36.11 Shared World Model

多机器人可共同构建 map / semantic memory。挑战是 data association、坐标对齐、冲突 belief 与通信预算。

## 36.12 Agentic Multi-Robot Collaboration

2026 Gemini Robotics 2 展示了多机器人协作，意味着 foundation models 开始承担：任务分工、状态共享、执行协调与动态 replan。

但真正科学评测应测试：

- team size 变化；
- agent capability 异质；
- communication dropout；
- single-agent failure；
- conflicting observations；
- new team composition。

## 36.13 Multi-Robot Foundation Model

一个基础模型可以共享高层 representation，但每个 robot 的 morphology 和 local controller 不同：

\[
z_{shared}=F(o_1,\ldots,o_N,g),
\qquad
 a_i=\pi_i(z_{shared},e_i,o_i).
\]

这种“共享语义/世界模型 + embodiment-specific execution”可能比统一所有 action 更可扩展。

---

# 能力层统一图

```text
                     task / human intent
                            ↓
                 reasoning + shared memory
                            ↓
      ┌─────────── skill / subgoal allocation ───────────┐
      │                  │                  │             │
 navigation         manipulation        locomotion   collaboration
      │                  │                  │             │
 base control      arms/hands/touch    whole body   multi-agent comm
      └──────────────────┴──────────────────┴─────────────┘
                            ↓
                  physical environment
                            ↑
            perception / force / tactile / human
```

不同“能力”最终不是独立模型，而是共享同一个 world state、memory、safety 和 learning loop。

## 必做实验

1. rigid push：改变 friction / mass，测 policy 泛化；
2. grasp：加入 reachability/collision 后比较 grasp-only score；
3. contact insertion：position control vs impedance + force；
4. 双臂 handover：纯视觉 vs force/tactile release condition；
5. cloth/cable：分析 rigid-state representation 的失败；
6. ObjectNav：semantic map vs reactive policy；
7. quadruped/humanoid locomotion：domain randomization ablation；
8. loco-manipulation：分层 controller vs unified policy；
9. multi-robot task allocation：通信延迟/断线测试；
10. long-horizon household task：记录完整 failure taxonomy。

## 延伸资料

- Lynch & Park, *Modern Robotics*.
- Bicchi & Kumar, robotic grasping / dexterous manipulation literature.
- Khatib, operational-space / whole-body control.
- Legged Gym / Isaac Lab locomotion ecosystems.
- Habitat / BEHAVIOR / OmniGibson embodied environments.
- NVIDIA GR00T N1.6 — https://research.nvidia.com/labs/gear/gr00t-n1_6/
- Google DeepMind Gemini Robotics 2 — https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Figure Helix — https://www.figure.ai/news/helix
