---
title: World Model / VLA / Embodied AI Datasheet v1.0
tags: [ai, world-model, vla, robotics, embodied-ai, control, policy, planning]
updated: 2026-10-01
---

# World Model / VLA / Embodied AI Datasheet v1.0

> A digital agent selects tool calls. An embodied system must select actions that **change a dynamic world** under delay, noise, partial observability, and physical consequences. World models learn the “plant”; VLAs learn a multimodal policy over that world.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md), [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md).

---

# 1. Translation into control engineering

Classical system:

\[
x_{t+1}=f(x_t,u_t)+w_t
\]

\[
y_t=h(x_t)+v_t
\]

where:

- \(x_t\): state;
- \(u_t\): control;
- \(y_t\): observation;
- \(w_t,v_t\): noise.

Learned world model:

\[
\hat x_{t+1}=f_\theta(\hat x_t,u_t)
\]

or probabilistically:

\[
p_\theta(x_{t+1}|x_t,u_t)
\]

The central analogy:

\[
\boxed{World\ Model\approx Learned\ Plant\ Model}
\]

---

# 2. Model-free vs model-based policy

## Model-free

\[
a_t\sim\pi_\theta(a|o_t)
\]

Does not explicitly require prediction of the next state.

## Model-based

\[
\hat s_{t+1}=f_\theta(s_t,a_t)
\]

The policy/planner can imagine consequences before acting.

---

# 3. Partial observability

A robot/agent rarely observes the true state:

\[
o_t\sim p(o_t|s_t)
\]

We need to infer a belief/latent state:

\[
b_t=P(s_t|o_{1:t},a_{1:t-1})
\]

or a recurrent embedding:

\[
z_t=F(z_{t-1},o_t,a_{t-1})
\]

This approaches the POMDP formulation.

---

# 4. World-model components

Idealized architecture:

\[
o_t\xrightarrow{Encoder}z_t
\]

\[
(z_t,a_t)\xrightarrow{Dynamics}\hat z_{t+1}
\]

\[
\hat z_{t+1}\xrightarrow{Decoder}\hat o_{t+1}
\]

Optionally:

\[
(z_t,a_t)\rightarrow \hat r_t
\]

\[
z_t\rightarrow \hat v_t
\]

---

# 5. Pixel-space vs latent world model

## Pixel-space

Predicts future image/video:

\[
p(I_{t+1:t+H}|I_{\le t},a_{t:t+H})
\]

Pros:

- interpretable;
- provides future visual evidence.

Cons:

- expensive;
- must model perceptual details irrelevant to control.

## Latent-space

\[
z_{t+1}=f_\theta(z_t,a_t)
\]

Pros:

- compression;
- focuses on useful features.

Cons:

- latent state can hide physical error;
- harder to audit.

---

# 6. Deterministic vs stochastic dynamics

Deterministic:

\[
\hat s_{t+1}=f_\theta(s_t,a_t)
\]

Probabilistic:

\[
s_{t+1}\sim p_\theta(s|s_t,a_t)
\]

Real worlds have multiple plausible futures.

When uncertainty matters, a single mean prediction can be dangerous:

\[
E[s_{t+1}]\notin feasible\ states
\]

for multimodal distributions.

---

# 7. Multi-step rollout

\[
\hat s_{t+k}=f_\theta(\hat s_{t+k-1},a_{t+k-1})
\]

Recursive error:

\[
e_{t+k}\approx F(e_{t+k-1},model\ error)
\]

As horizon grows:

\[
H\uparrow\Rightarrow accumulated\ model\ error\uparrow
\]

not necessarily linearly.

---

# 8. Planning / MPC analogy

We want:

\[
a^*_{t:t+H-1}
=
\arg\max_{a_{t:t+H-1}}
\sum_{k=0}^{H-1}\gamma^kR(\hat s_{t+k},a_{t+k})
\]

Typically, only the first action is executed before replanning:

\[
MPC: plan\rightarrow act\rightarrow observe\rightarrow replan
\]

This is the direct bridge to model-predictive control.

---

# 9. Search over actions

## Sampling

Sample \(N\) action sequences:

\[
A^{(1)},\ldots,A^{(N)}
\]

Evaluate predicted return:

\[
J(A^{(i)})
\]

Choose the best.

## CEM-like optimization

Iteratively update the action distribution from elite samples.

## Gradient planning

If dynamics/reward are differentiable:

\[
\nabla_AJ
\]

can optimize the action sequence directly.

---

# 10. Vision-Language-Action — VLA

Input:

\[
C_t=
\{vision_t,language,state/proprioception_t,history\}
\]

Policy:

\[
a_t\sim\pi_\theta(a|C_t)
\]

A VLA is not simply a VLM plus a tool-call button: its action space may be continuous, temporal, and constrained by physical dynamics.

---

# 11. Action representation

## Continuous

Example manipulator:

\[
a_t=(\Delta x,\Delta y,\Delta z,\Delta r_x,\Delta r_y,\Delta r_z,g)
\]

## Discretized tokens

Each dimension is quantized:

\[
a_t\rightarrow(token_1,\ldots,token_m)
\]

This enables an autoregressive categorical decoder.

## Action chunks

\[
A_t=(a_t,a_{t+1},\ldots,a_{t+K-1})
\]

This reduces backbone call frequency and may smooth control.

---

# 12. Action-chunking trade-off

Larger chunks:

\[
K\uparrow
\Rightarrow
InferenceFrequency\downarrow
\]

but:

\[
FeedbackFrequency\downarrow
\]

So there is a trade-off between throughput and closed-loop responsiveness.

In control terms:

> a longer open-loop interval saves compute but increases exposure to model mismatch and disturbances.

---

# 13. Autoregressive action policy

\[
P(A)=\prod_tp(a_t|a_{<t},C)
\]

Pros:

- compatible with causal Transformers;
- simple.

Cons:

- sequential latency;
- error propagation;
- continuous actions require tokenization or mixture outputs.

---

# 14. Diffusion policy

Noisy action trajectory:

\[
a_\tau=\alpha_\tau a_0+\sigma_\tau\epsilon
\]

Observation-conditioned denoising:

\[
a_{\tau}\rightarrow a_{\tau-1}\rightarrow\cdots\rightarrow a_0
\]

Advantage: models multimodal distributions over continuous trajectories.

Cost: multiple network evaluations.

---

# 15. Flow-matching action policy

\[
\frac{da_\tau}{d\tau}=v_\theta(a_\tau,\tau,C)
\]

Generates action trajectories by integrating a vector field.

WorldFly 2026 is an example of a dual-branch flow-matching mechanism that jointly generates future visual prediction and navigation actions.

---

# 16. Joint world-action generation

Instead of:

\[
WorldModel\rightarrow Planner
\]

we can use a coupled model:

\[
(C_t,noise)
\rightarrow
(\hat Video_{future},A_{future})
\]

Future generation acts as “imagination” shared with the policy.

This reduces modular separation, but also makes debugging harder.

---

# 17. Vision-language grounding for action

Instruction:

> “pick up the red key on the right”

requires:

\[
Language\rightarrow Object\ Identity
\]

\[
Vision\rightarrow Object\ Localization
\]

\[
Localization\rightarrow Reachable\ Pose
\]

\[
Pose\rightarrow Action\ Trajectory
\]

An error at any stage may look like “policy failure.”

---

# 18. State/action frequency

Control systems have clocks.

If observation rate is:

\[
f_o=30Hz
\]

and policy rate is:

\[
f_\pi=5Hz
\]

each decision covers approximately:

\[
\frac{f_o}{f_\pi}=6
\]

observation frames.

Total latency must fit the dynamics of the controlled system.

---

# 19. Latency budget

Closed-loop delay:

\[
T_{loop}
=T_{sense}+T_{encode}+T_{policy}+T_{decode}+T_{actuate}
\]

If \(T_{loop}\) is large relative to the system time constant, the policy acts on stale state.

Control mathematics matters more than “tokens/s.”

---

# 20. Safety envelope

Proposed action:

\[
a_t^{raw}=\pi(s_t)
\]

Safety filter:

\[
a_t=\Pi_{\mathcal A_{safe}}(a_t^{raw})
\]

May include:

- joint limits;
- collision constraints;
- velocity/acceleration limits;
- workspace boundaries;
- human proximity;
- forbidden actions.

A safe policy should not depend on prompting alone.

---

# 21. Human in the loop vs supervisory control

HITL does not need to approve every action.

It can operate at the supervisory level:

\[
Human\rightarrow Goal/Mode/Constraint
\]

\[
Controller\rightarrow LowLevelActions
\]

This division is more compatible with high-frequency systems.

---

# 22. Sim-to-real gap

Training in simulation:

\[
p_{sim}(s,a)
\]

Deployment:

\[
p_{real}(s,a)
\]

If:

\[
p_{sim}\neq p_{real}
\]

the policy experiences domain shift.

Techniques:

- domain randomization;
- real-data fine-tuning;
- adaptation;
- robust-control constraints.

---

# 23. World-model error decomposition

## Perception error

\[
e_{enc}
\]

## Transition error

\[
e_{dyn}
\]

## Reward/value error

\[
e_R,e_V
\]

## Planning/search error

\[
e_{plan}
\]

## Actuation/model mismatch

\[
e_{act}
\]

Result:

\[
e_{task}=F(e_{enc},e_{dyn},e_R,e_{plan},e_{act})
\]

Changing the policy does not automatically fix a bad encoder.

---

# 24. Metrics

- success rate;
- episode return;
- collision rate;
- intervention rate;
- action latency;
- path efficiency;
- pose error;
- future prediction error;
- calibration/uncertainty;
- real-time factor;
- horizon before rollout divergence.

---

# 25. Failure surfaces

- hallucinated affordance;
- perception/action mismatch;
- temporal lag;
- compounding rollout error;
- action-discretization artifacts;
- overly long open-loop chunk;
- multimodal alignment failure;
- reward misspecification;
- sim-to-real shift;
- safety filter fighting policy;
- partial observability;
- multimodal future collapse.

---

# 26. Digital agent vs VLA

## Digital agent

\[
Action\in\{API,click,key,type,tool\}
\]

with an environment that is often transactional and observable through software.

## VLA

\[
Action\in\mathbb R^m\text{ or trajectory}
\]

with a continuous, noisy, partially observable environment that may contain irreversible states.

See [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) for the digital side of the boundary.

---

# 27. SOTA Snapshot 2026

The central trend is convergence around:

\[
World\ Model + VLA
\]

into models that **jointly imagine future perception and action**.

WorldFly illustrates coupled flow matching for future video + navigation action in UAVs, using world modeling specifically to handle occlusions and viewpoint transitions.

The broader engineering insight is:

> a competent embodied system must model not only “what should I do?” but **how the world is likely to respond**.

---

# 28. Dissection checklist

1. What is the observation \(o_t\)?
2. Is there a latent/belief state?
3. Does the model learn transition dynamics?
4. Is the future represented in pixels or latents?
5. Is the dynamics model deterministic or probabilistic?
6. What rollout horizon is usable before divergence?
7. Is the policy AR, diffusion, or flow?
8. Is the action space continuous or tokenized?
9. Does it generate one action or action chunks?
10. What is the closed-loop frequency?
11. What is end-to-end latency?
12. Is there a separate planner?
13. Is there a hard safety layer?
14. What is the sim-to-real gap?
15. How does uncertainty enter decision-making?

---

# Snapshot references

- WorldFly: A World-Model-Based Vision-Language-Action Model for UAV Navigation — https://arxiv.org/abs/2606.06147
