---
title: Video Generation — Spatiotemporal Latent Datasheet v2.0
tags: [ai, video, diffusion, flow, temporal, dit]
updated: 2026-10-01
---

# Video Generation — Spatiotemporal Latent Datasheet v2.0

> Video is not “image + motion slider.” It is generation over a compressed spatiotemporal state, where identity, geometry, camera, motion, and sometimes audio must remain coherent across \(T\).

## 1. Fundamental tensor

Pixels:

\[
X\in\mathbb{R}^{B\times T\times H\times W\times C}
\]

After a spatiotemporal codec/VAE:

\[
Z\in\mathbb{R}^{B\times T_l\times H_l\times W_l\times C_l}
\]

---

## 2. Spatial and temporal compression

Define:

\[
r_s=\frac{H}{H_l}=\frac{W}{W_l}
\]

\[
r_t=\frac{T}{T_l}
\]

The stronger the compression, the lower the denoiser/DiT cost, but the more work the decoder must do to reconstruct detail and motion.

### Insight

Observable resolution such as `1920×1080×N frames` is not the dimensionality directly processed by the core model; cost depends on the **latent token count**.

---

## 3. Patchification

If the latent is patchified:

\[
N=T_pH_pW_p
\]

Naive global attention:

\[
O(N^2)
\]

That is why video needs:

- temporal compression;
- factorized attention;
- windowing;
- sparse attention;
- FlashAttention;
- sequence parallelism.

---

# PART I — GENERATION TOPOLOGY

## 4. Full-sequence generation

All frames/latents belong to the same state:

\[
Z_t=[z_t^1,z_t^2,\ldots,z_t^T]
\]

The model may denoise/transport the sequence jointly.

### Consequence

There is no mathematical law saying “the last frame is always worse.”

---

## 5. Causal/chunked/continuation generation

When future blocks explicitly depend on previous outputs:

\[
Z_{chunk,k+1}\sim p(Z\mid Z_{chunk,\le k},C)
\]

errors may accumulate:

\[
e_{k+1}=f(e_k,\ldots)
\]

Here, accumulated temporal drift is a genuine structural concern.

---

# PART II — MOTION AND COHERENCE

## 6. Motion is not a universal variable

`motion_bucket_id`/`motion score` exist in specific model families. The universal physical concept is the **magnitude/complexity of the temporal transformation** required by conditioning.

The greater the:

- displacement;
- deformation;
- occlusion/disocclusion;
- viewpoint change;
- multi-object interaction;

the harder it is to maintain temporal correspondence.

### Heuristic, not a law

\[
Motion\ complexity\uparrow\Rightarrow Coherence\ risk\uparrow
\]

but the strength of that relationship depends on architecture and training.

---

## 7. Optical-flow mental model

For a point/feature:

\[
(x_t,y_t)\rightarrow(x_{t+1},y_{t+1})
\]

The model must infer simultaneously:

- correspondence;
- visibility;
- deformation;
- appearance consistency;
- new content in disoccluded areas.

“Melting” is an identity/correspondence failure, not simply “too much noise.”

---

# PART III — CONDITIONING

## 8. Text-to-video

\[
C=C_{text}
\]

### Image-to-video

\[
C=\{C_{text},C_{image}\}
\]

### Start/end/keyframe conditioning

\[
C=\{frame_{start},frame_{end},keyframes,\ldots\}
\]

### Camera conditioning

May be represented by:

- text;
- trajectory embedding;
- pose matrices;
- flow/depth/control representation.

“Pan/zoom” as a button is UI/pipeline; camera trajectory is the general concept.

---

## 9. Noise augmentation in I2V

Some pipelines add noise to the reference before conditioning/continuation.

This increases freedom, but it is not universally parameterized on `0..1`.

Classify it as `MODEL/PIPE`.

---

# PART IV — GUIDANCE

## 10. CFG in video

Same general formulation:

\[
f_g=f_u+s(f_c-f_u)
\]

but now \(f\) acts over a spatiotemporal tensor.

High guidance can increase prompt adherence while also amplifying inconsistency, oversharpening, or flicker depending on the model.

---

## 11. Spatio-Temporal Guidance — STG

Modern pipelines may create a “degraded” prediction by perturbing self-attention/blocks and push the trajectory away from it:

\[
f_{guided}=f_{base}+s_{stg}(f_{base}-f_{perturbed})
\]

The idea is to strengthen spatiotemporal structure/coherence using a differential direction, analogous in spirit to CFG but based on a different perturbation.

LTX-2.x exposes STG as an explicit control.

---

## 12. Modality Isolation Guidance

In joint video+audio models, one prediction may be obtained with cross-modality attention disabled and used as a weak reference:

\[
f_{guided}=f+ s_m(f-f_{isolated})
\]

This shows that guidance is a general family of **contrasts between predictions**, not merely positive prompt vs negative prompt.

---

# PART V — FPS

## 13. Observable FPS vs latent temporal rate

FPS is an output property:

\[
Duration=Frames/FPS
\]

But model cost depends on \(T_l\), not directly on final FPS when temporal compression/interpolation is involved.

### Do not confuse

- generating 60 actual frames;
- generating 15 frames + 4× interpolation;
- generating temporally compressed latents and decoding 60 frames.

These are mathematically different pipelines.

---

## 14. Frame interpolation

A separate model may estimate intermediate frames:

\[
I_{t+\alpha}=F(I_t,I_{t+1},\alpha)
\]

This does not add original temporal information from the generative core in the same way as generating additional latent frames.

---

# PART VI — DURATION AND WINDOWING

## 15. Duration

\[
T=FPS\cdot duration
\]

But latent frames:

\[
T_l\approx T/r_t
\]

Long videos may use windows:

\[
W_1,W_2,\ldots,W_k
\]

with overlap:

\[
|W_i\cap W_{i+1}|>0
\]

More overlap increases continuity and compute.

---

## 16. Drift in long-form generation

Possible causes:

- causal chunking;
- context truncation;
- reference refresh;
- accumulation of generated conditioning;
- weak identity representation;
- shot changes.

The correct solution depends on topology, not a rule such as “cut off the last second.”

---

# PART VII — CAMERA

## 17. Camera vs object motion

Ideally decompose:

\[
Motion_{observed}=Motion_{camera}+Motion_{objects}+deformation
\]

Prompting everything as one sentence leaves the model to infer that decomposition. Control representations can reduce ambiguity.

---

# PART VIII — COMPUTE

## 18. Token count

\[
N=T_pH_pW_p
\]

Double the duration while holding everything else constant:

\[
N\approx2N
\]

Naive global attention:

\[
N^2\rightarrow4N^2
\]

That is the structural reason for compression and factorized attention.

---

## 19. Guidance cost

CFG + STG + modality guidance may require multiple forward passes per step.

\[
Cost\approx NFE\times passes_{guidance}\times C_{forward}
\]

A guidance slider may therefore change both **quality and cost**.

---

# PART IX — COUPLING MATRIX

| Control ↑ | Motion freedom | Temporal coherence | Compute | Identity |
|---|---:|---:|---:|---:|
| duration | — | risk ↑ | ↑ sharply | risk ↓ |
| resolution | — | indirect risk | ↑ sharply | potential ↑ |
| I2V reference weight | ↓ | ↑ | varies | ↑ |
| CFG | adherence ↑ | non-monotonic | ↑ | may ↑/↓ |
| STG | — | potential ↑ | ↑ | potential ↑ |
| overlap | — | ↑ | ↑ | ↑ |
| interpolation | smoothness ↑ | does not create identity | ↑ post | ~ |

---

# PART X — COMFYUI

## 20. Nodes to look for conceptually

- video VAE/codec;
- frame/latent dimensions;
- model/DiT;
- text/reference conditioning;
- sampler/scheduler;
- CFG/STG/custom guider;
- continuation/keyframe controls;
- VAE decode;
- interpolation/upscale.

A parameter that looks like “motion” may actually implement conditioning, noise augmentation, temporal scheduling, or merely a prompt convention. Check the node/model documentation.

---

# PART XI — DIAGNOSTICS

| Symptom | Investigate |
|---|---|
| face drift | identity conditioning/windowing/model |
| flicker | temporal model/guidance/decoder |
| camera “melts” the scene | camera conditioning + motion complexity |
| final chunk degrades | causal continuation/error accumulation |
| OOM | T×H×W latent tokens / activations |
| audio out of sync | cross-modal conditioning/guidance |

---

## 21. Snapshot 2026

LTX-2.x exposes a modern video+audio stack with DiT, CFG, STG, and modality-isolation guidance separated by modality. It is a good demonstration of why the old “motion score + CFG + FPS” model no longer describes the whole machine.

## References

- LTX-2 Diffusers — https://huggingface.co/docs/diffusers/main/api/pipelines/ltx2
- CogVideoX — https://arxiv.org/abs/2408.06072
