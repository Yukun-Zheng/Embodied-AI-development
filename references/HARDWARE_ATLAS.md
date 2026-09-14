# Robot & Hardware Atlas

> Hardware is not a neutral carrier of intelligence. This atlas organizes robot platforms by morphology, actuation, sensing, control interface and research suitability.

# 1. Why hardware belongs inside an AI textbook

A policy does not act on an abstract vector. It ultimately drives a physical mechanism with bandwidth, backlash, torque limits, thermal constraints, latency and safety boundaries.

A useful decomposition is:

```text
policy action
→ command interface
→ low-level controller
→ actuator
→ transmission
→ joint/link motion
→ contact
→ sensor feedback
```

Two robots with identical kinematic topology can behave very differently because the dynamics below the policy interface differ.

---

# 2. Hardware description axes

Every robot platform should be summarized by:

| Axis | Examples |
|---|---|
| morphology | arm, bimanual, mobile manipulator, quadruped, humanoid, dexterous hand |
| DOF | fixed-base vs floating-base, active/passive joints |
| actuation | servo, harmonic drive, QDD, tendon, pneumatic |
| sensing | encoder, current, torque, IMU, FT, tactile, RGB-D |
| control interface | position, velocity, torque, Cartesian target |
| low-level rate | e.g. hundreds to thousands of Hz |
| policy rate | typically lower |
| compute | external workstation, onboard GPU, embedded SoC |
| communication | EtherCAT, CAN, serial, Ethernet |
| safety | limits, brakes, collision detection, e-stop |
| openness | URDF/MJCF/USD, SDK, firmware/control access |

---

# 3. Fixed-base manipulators

## Franka-class research arms

Strengths:

- torque-aware control;
- impedance control;
- widely used in manipulation research;
- mature simulation models.

Useful for:

- contact-rich manipulation;
- impedance / operational-space control;
- imitation learning;
- VLA benchmarking.

Limitations:

- fixed-base tabletop assumptions;
- cannot study whole-body mobility;
- end-effector/gripper often dominates task capability.

## UR-class industrial arms

Strengths:

- mature industrial deployment;
- repeatability;
- broad tooling ecosystem.

Research value:

- deployment engineering;
- calibration;
- trajectory execution;
- industrial manipulation.

Less suitable when full torque-level access or highly compliant interaction is required.

---

# 4. Bimanual platforms

Bimanual systems introduce an additional relative configuration:

\[
T_{L}^{R}=T_{L}^{W}T_{W}^{R}.
\]

Hardware-specific issues:

- inter-arm calibration;
- self-collision geometry;
- synchronized control clocks;
- shared object force distribution;
- asymmetric gripper capability.

Representative research setups include ALOHA-style low-cost teleoperation systems and higher-end dual-arm industrial/research platforms.

When comparing bimanual algorithms, report whether both arms share:

- the same control rate;
- the same gripper;
- the same camera visibility;
- the same kinematic workspace.

---

# 5. Mobile manipulators

A mobile manipulator combines base and arm state:

\[
q = [q_{base}, q_{arm}, q_{gripper}].
\]

The main hardware question is whether the system is treated as:

```text
base planner + arm policy
```

or as one coupled whole-body controller.

Research questions:

- navigation/manipulation handoff;
- base-arm coordination;
- camera viewpoint control;
- dynamic reachability;
- cable/battery/compute constraints.

---

# 6. Quadrupeds

Quadruped hardware highlights floating-base dynamics and contact scheduling.

Important properties:

- leg torque bandwidth;
- foot contact sensing;
- IMU quality;
- mechanical compliance;
- onboard compute;
- battery power and thermal envelope.

A locomotion policy trained on a robot with high torque density may not transfer to a weaker actuator system even when geometry is similar.

---

# 7. Humanoids

Humanoid platforms require the full stack:

```text
floating base
+ legs
+ torso
+ arms
+ hands/grippers
+ head/sensors
```

The research-relevant distinction is not just DOF count.

Compare:

- actuator torque density;
- backdrivability;
- walking speed;
- whole-body control interface;
- hand dexterity;
- perception placement;
- battery/runtime;
- fall tolerance;
- teleoperation capability.

A humanoid with simple parallel grippers and a humanoid with dexterous hands should not be treated as the same manipulation embodiment.

---

# 8. Dexterous hands

Dexterous hands amplify three issues:

1. high-dimensional action;
2. contact observability;
3. actuation/transmission complexity.

Common mechanisms:

- direct motorized joints;
- tendon-driven fingers;
- underactuated fingers;
- coupled joints.

The effective action dimension can differ from nominal DOF count.

Tactile sensing can be:

- fingertip force;
- taxel arrays;
- vision-based tactile;
- strain-based sensing.

The interface must be documented before comparing learning methods.

---

# 9. Grippers

A two-finger gripper can be controlled as:

- binary open/close;
- width target;
- velocity;
- force;
- continuous grasp effort.

This seemingly small design choice changes the action distribution.

A benchmark should therefore not write only `gripper: 1D`; it should specify semantics and physical controller.

---

# 10. Cameras and sensor placement

The same camera can produce very different observability depending on placement.

### fixed third-person camera
Advantages:

- stable frame;
- broad scene coverage.

Disadvantages:

- occlusion by robot/object;
- poor egocentric detail.

### wrist camera
Advantages:

- local manipulation detail;
- view moves with end effector.

Disadvantages:

- nonstationary extrinsics;
- motion blur;
- limited global context.

### head camera
Important for humanoids/mobile systems because sensing becomes coupled to whole-body motion.

---

# 11. Compute placement

## External compute

```text
robot ↔ Ethernet ↔ workstation/server
```

Advantages:

- powerful GPU;
- easy development.

Risks:

- network latency;
- packet loss;
- synchronization.

## Onboard compute

Advantages:

- lower communication latency;
- autonomy.

Constraints:

- power;
- thermal;
- memory;
- weight.

On-device foundation policy research is fundamentally a hardware-software co-design problem.

---

# 12. Multi-rate hardware stack

A realistic system often looks like:

```text
motor current loop       5–20 kHz
joint servo              500–2000 Hz
state estimator          100–1000 Hz
whole-body controller    100–500 Hz
camera                    20–60 Hz
VLA / large policy       2–30 Hz
planner / language       0.1–5 Hz
```

These rates are illustrative, not universal.

A single “policy frequency” does not describe the system.

---

# 13. Hardware-induced distribution shift

Even if two robots have identical observations and nominal action spaces, transition dynamics differ:

\[
p_i(s_{t+1}\mid s_t,a_t) \neq p_j(s_{t+1}\mid s_t,a_t).
\]

Sources:

- gear ratio;
- friction;
- latency;
- motor strength;
- controller gains;
- compliance;
- link inertia;
- sensor noise.

This is why cross-embodiment transfer is partly a dynamics-transfer problem.

---

# 14. Hardware card template

Every platform page should record:

```text
Robot:
Version:
Morphology:
DOF:
Actuator type:
Transmission:
Nominal torque / speed limits:
Control interfaces:
Low-level rate:
Onboard sensors:
External sensors:
Compute:
Communication buses:
URDF/MJCF/USD availability:
SDK/control openness:
Safety mechanisms:
Typical policy rate:
Known latency:
Known calibration issues:
Tasks it is well-suited for:
Claims it cannot support:
```

---

# 15. Hardware–intelligence co-design

The long-term research question is not:

> what is the strongest policy for this robot?

but also:

> what body and control interface make learning easier, safer and more general?

Examples:

- compliant actuation can simplify contact;
- tactile sensors can reduce visual ambiguity;
- movable cameras can convert perception uncertainty into an action problem;
- torque sensing can enable safer interaction;
- modular limbs can expose morphology adaptation.

The body is therefore not merely a deployment target. It is part of the computational system.
