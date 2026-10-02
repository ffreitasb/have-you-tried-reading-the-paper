---
title: Multimodal / VLM / Omni Model Datasheet v1.0
tags: [ai, multimodal, vlm, omni, vision-language, audio-language, inference]
updated: 2026-10-01
---

# Multimodal / VLM / Omni Model Datasheet v1.0

> Multimodality is not “an LLM that accepts images.” It is the engineering problem of **turning signals with incompatible topologies, resolutions, and clocks into states that can interact inside the same system**.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 1. The fundamental problem

Consider modalities:

```math
X=\{X_t,X_v,X_a,X_{vid}\}
```

with:

- text: discrete sequence;
- image: 2D grid;
- audio: waveform / spectrogram / codec sequence;
- video: 2D grid + time.

The system must construct compatible representations:

```math
Z_m=E_m(X_m)
```

followed by some fusion operation:

```math
H=\mathcal F(Z_t,Z_v,Z_a,Z_{vid})
```

The key question is not “what prompt should I use?” but:

```math
\boxed{How\ does\ each\ modality\ become\ shareable\ state?}
```

---

# 2. Multimodal topologies

## 2.1 Encoder + projector + LLM

Classic VLM form:

```math
Image\xrightarrow{VisionEncoder}Z_v
\xrightarrow{Projector}Z'_v
\rightarrow LLM
```

If:

```math
Z_v\in\mathbb R^{N_v\times d_v}
```

but the backbone uses hidden size $`d_h`$:

```math
Z'_v=Z_vW_p,
\quad
W_p\in\mathbb R^{d_v\times d_h}
```

The projector may be:

- linear;
- MLP;
- convolutional/downsampler;
- learned-query resampler;
- attention bridge.

### Failure surface

A huge backbone with a weak bridge still creates a bottleneck:

```math
Information(X_v)\gg Information(Z'_v)
```

The information loss has already happened before the LLM sees anything.

---

## 2.2 Cross-attention bridge

Text queries visual/audio features:

```math
Q=H_{text}W_Q
```

```math
K=Z_vW_K,\quad V=Z_vW_V
```

```math
A=softmax\left(\frac{QK^T}{\sqrt d}\right)V
```

Advantage: the full modality does not need to be serialized into “text-equivalent tokens.”

Trade-off: additional modules, state, and cross-attention cost.

---

## 2.3 Joint / early fusion

All modalities enter one shared sequence/state:

```math
H_0=[Z_t;Z_v;Z_a;Z_{vid}]
```

The backbone learns interactions directly.

### Cost

If global attention is used:

```math
N_{total}=N_t+N_v+N_a+N_{vid}
```

```math
C_{attn}\sim O(N_{total}^2)
```

So every modality competes for the same context budget.

---

## 2.4 Late fusion

Each modality is processed more deeply before combination:

```math
H=Fuse(f_t(X_t),f_v(X_v),f_a(X_a))
```

Pros:

- specialization;
- less early interference.

Cons:

- alignment between representations may be harder;
- cross-modal interaction happens later.

---

## 2.5 Omni / Thinker–Talker style

Omni systems may separate:

```math
Perception/Reasoning\rightarrow Thinker
```

```math
Speech/Audio\ Generation\rightarrow Talker
```

while sharing context/representations.

Output may be interleaved:

```math
Text\ tokens + Speech\ codec\ tokens
```

or produced through multiple heads.

---

# 3. Vision tokenization

## 3.1 Patchification

Image:

```math
X\in\mathbb R^{H\times W\times C}
```

Patch size $`P_h\times P_w`$:

```math
N_v\approx
\frac{H}{P_h}\frac{W}{P_w}
```

Idealized 1024² image, patch 16:

```math
N_v=64^2=4096
```

before pooling/merging.

This explains why “one image” may consume thousands of internal positions.

---

## 3.2 Dynamic resolution

Instead of fixed resizing, modern systems may adapt patch count to aspect ratio/resolution.

State:

```math
N_v=f(H,W,P,budget)
```

### Consequence

Two images can have very different context cost even if both count as “one image” at the UI level.

---

## 3.3 Patch merging / token compression

Grouping $`k\times k`$:

```math
N'_v\approx\frac{N_v}{k^2}
```

Trade-off:

```math
TokenBudget\downarrow
\leftrightarrow
SpatialDetail\downarrow
```

There is no free compression.

---

# 4. Video inside a VLM

Without compression:

```math
N_{vid}\approx
T_f\frac{H}{P_h}\frac{W}{P_w}
```

where $`T_f`$ is the number of sampled frames.

Even 1 fps can create enormous sequence length for long video.

## Strategies

- frame subsampling;
- temporal pooling;
- tubelets;
- temporal patchification;
- hierarchical summarization;
- memory/compression tokens;
- long-context sparse attention.

### Rule

```math
VideoDuration\uparrow
\not\Rightarrow
FramesProcessed\uparrow\ linearly
```

because pipelines may change sampling rate or compress adaptively.

---

# 5. Audio inside multimodal models

Possible representations:

- log-Mel frames;
- continuous encoder states;
- semantic audio tokens;
- codec tokens;
- compressed summary tokens.

If the frontend produces $`r_a`$ states/s:

```math
N_a=r_aD
```

for duration $`D`$.

Long-form audio is therefore a **sequence-compression** problem, not just a temporal-window problem.

See [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

---

# 6. Multimodal positional systems

Text has 1D position:

```math
p_t=t
```

Image has:

```math
p_v=(x,y)
```

Video:

```math
p_{vid}=(t,x,y)
```

Audio:

```math
p_a=t_{physical}
```

Multimodal models must encode a relation:

```math
R(position_i,position_j)
```

that preserves the relevant structure.

## Modality ≠ position

In addition to position, the backbone often needs to know **which modality a token came from**:

```math
h_i=e_i+p_i+m_i
```

or through modulation/segment embeddings.

---

# 7. Time alignment

In audiovisual dialogue:

```math
Audio(t)\leftrightarrow Video(t)
```

A spoken word should align with the corresponding movement/object.

Problems:

- different clocks;
- different frame rates;
- codec delay;
- resampling;
- chunk boundaries.

An omni system needs some shared temporal map:

```math
\tau_m(i)\rightarrow t_{global}
```

### Failure surface

If temporal alignment fails, the model may correctly identify **what** happened while associating it with the wrong frame/event.

---

# 8. Spatial grounding

Generic visual understanding:

```math
Image\rightarrow semantics
```

Grounding requires:

```math
Text\ phrase\rightarrow region/bbox/point
```

Bounding box:

```math
b=(x_{min},y_{min},x_{max},y_{max})
```

It may be represented as:

- discretized tokens;
- continuous coordinates;
- special location vocabulary;
- segmentation masks.

The ability to “see” and the ability to **localize** are not equivalent.

---

# 9. Interleaved multimodality

In mixed sequences:

```text
[text] [image] [text] [image] [audio] [text]
```

context order itself carries semantics.

The model must preserve relationships such as:

```math
reference("second\ image")\rightarrow Z_{v,2}
```

This problem combines:

- multimodal positional identity;
- long-context reference tracking;
- modality boundaries.

---

# 10. Multimodal output

## Text output

```math
H\rightarrow LMHead\rightarrow tokens
```

## Speech output

```math
H\rightarrow SpeechHead/Talker\rightarrow codec/latent\rightarrow waveform
```

## Image/video output

A separate generative backbone may be conditioned by the understanding/reasoning model:

```math
H_{reasoning}\rightarrow C_{generator}\rightarrow Diffusion/Flow
```

So “a multimodal model” may actually be **a system of multiple operators**, not one monolithic network.

---

# 11. Multimodal token accounting

For runtime:

```math
T_{effective}
=
T_{text}
+N_v
+N_a
+N_{vid}
+N_{special}
```

If the causal backbone builds KV for all of it:

```math
M_{KV}\propto T_{effective}
```

This is one of the most useful equations in practice.

### Translation into engineering terms

Adding one image may cost more memory/context than thousands of words.

---

# 12. Cross-modal attention cost

If text length $`N_t`$ queries visual length $`N_v`$:

```math
C_{cross}\sim O(N_tN_vd)
```

If everything is fused under global self-attention:

```math
C_{joint}\sim O((N_t+N_v)^2d)
```

Architecture determines the physical cost curve.

---

# 13. Multimodal training objectives

Possible components:

### Contrastive

```math
L_{contrastive}
```

aligns representations.

### Caption/next-token

```math
L_{LM}
```

teaches description/response.

### Reconstruction/generation

```math
L_{gen}
```

### Grounding

```math
L_{ground}
```

### Audio-visual synchronization

```math
L_{sync}
```

Modern multimodal training may combine:

```math
L=\sum_i\lambda_iL_i
```

So “it is a VLM” does not reveal its actual objective function.

---

# 14. Failure surfaces

## 14.1 Modality dominance

One modality overrides the others.

Example: the model follows its textual prior even when the image contradicts the text.

## 14.2 Projector bottleneck

Details disappear in the bridge.

## 14.3 Token starvation

Aggressive compression loses small objects or visual text.

## 14.4 Token explosion

High resolution/video consumes context and memory.

## 14.5 Temporal desynchronization

Audio/video are semantically correct but temporally wrong.

## 14.6 Hallucinated grounding

Plausible semantics without real spatial evidence.

## 14.7 Cross-modal conflict

```math
C_{text}\neq C_{vision}
```

The model must arbitrate contradictory sources.

---

# 15. Controls vs observables

| Variable | Class | Effect |
|---|---|---|
| image resolution | `PIPE/INF` | changes visual token budget |
| frame sampling rate | `PIPE/INF` | changes temporal coverage and token count |
| max pixels / token budget | `PIPE/BACKEND` | caps cost |
| audio chunk length | `PIPE/INF` | latency ↔ acoustic context |
| projector type | `ARCH` | bridge capacity |
| vision encoder size | `ARCH/MODEL` | perceptual quality/cost |
| context length | `MODEL/BACKEND` | ceiling on joint state |
| modality dropout | `OBJ/TRAIN` | robustness to missing modalities |

Useful observables:

- tokens per image/frame/s;
- context occupancy;
- grounding accuracy;
- OCR accuracy;
- audio/video alignment error;
- first-token / first-audio latency;
- peak VRAM with/without encoder resident.

---

# 16. SOTA Snapshot — 2026-10-01

Qwen3.5-Omni exemplifies the convergence toward omni models with:

- text, vision, audio, and video;
- Thinker/Talker;
- hybrid MoE;
- long context;
- streaming speech;
- explicit audiovisual synchronization.

Qwen3-Omni had already demonstrated Thinker–Talker MoE and speech generation through codec tokens; the next generation expands scale/context and synchronization.

The important architectural point is not the brand: **omni models are making modality alignment + token compression + streaming state as central as the main Transformer itself**.

---

# 17. Checklist for dissecting any VLM/Omni model

1. Which encoder exists for each modality?
2. What token/state rate does it produce?
3. Is there a projector, resampler, or joint backbone?
4. What hidden dimension receives each modality?
5. How is spatial/temporal position encoded?
6. How many tokens does one image/video/second of audio consume?
7. Does the backbone see all modalities under the same self-attention?
8. Is there separate cross-attention?
9. Are there independent heads/talkers/decoders?
10. What state persists during streaming?
11. How are modality conflicts resolved?
12. What is the VRAM curve with resolution/duration?

---

# Snapshot references

- Qwen3.5-Omni Technical Report — https://arxiv.org/abs/2604.15804
- Qwen3-Omni Technical Report — https://arxiv.org/abs/2509.17765
- Qwen3-ASR Technical Report — https://arxiv.org/abs/2601.21337
