---
title: Image Generation — Diffusion, Flow & DiT Datasheet v2.0
tags: [ai, image, diffusion, rectified-flow, dit, comfyui]
updated: 2026-10-01
---

# Image Generation — Diffusion, Flow & DiT Datasheet v2.0

> The central variable is not “which sampler makes it look prettier.” It is **which latent state is being traversed, what quantity the network predicts, and which integrator turns that prediction into a trajectory**.

## 1. Canonical graph

\[
prompt/reference\rightarrow condition\ encoder\rightarrow latent\ state\rightarrow denoiser/vector\ field\rightarrow solver\ loop\rightarrow AE/VAE\ decoder\rightarrow pixels
\]

Typical pipeline:

\[
C\rightarrow x_T\rightarrow f_\theta(x_t,t,C)\rightarrow x_{t-1}\rightarrow\cdots\rightarrow x_0\rightarrow D(x_0)
\]

---

# PART I — REPRESENTATION

## 2. Pixel space vs latent space

Pixel space:

\[
X\in\mathbb{R}^{B\times 3\times H\times W}
\]

Latent space:

\[
Z=E(X)\in\mathbb{R}^{B\times C_l\times H_l\times W_l}
\]

With spatial compression factor \(f\):

\[
H_l\approx H/f,\qquad W_l\approx W/f
\]

Modern generation almost always saves compute by working in \(Z\), not directly in pixels.

### Consequence

Resolution increases the number of latent positions:

\[
N_l\propto H_lW_l
\]

For a Transformer using global attention over patches:

\[
C_{attn}\sim O(N^2)
\]

---

## 3. Autoencoder / VAE

Encoder:

\[
X\rightarrow Z
\]

Decoder:

\[
\hat X=D(Z)
\]

The decoder imposes a fidelity ceiling independent of the denoiser.

### Failure modes

- reconstruction blur;
- color shift;
- high-frequency loss;
- latent scaling mismatch;
- decoder incompatibility.

A “washed-out image” does not automatically prove the VAE is wrong; the cause may be conditioning, guidance, decoder behavior, or range mismatch.

---

# PART II — GENERATIVE PROCESS

## 4. Classical diffusion

Simplified forward process:

\[
x_t=\alpha_t x_0+\sigma_t\epsilon,\qquad \epsilon\sim\mathcal N(0,I)
\]

The network may predict:

- \(\epsilon\): noise prediction;
- \(x_0\): clean sample;
- \(v\): velocity parameterization;
- score \(\nabla_x\log p_t(x)\).

These parameterizations are not just UI labels; they change numerical scale and solver behavior.

---

## 5. Rectified flow / flow matching

Continuous trajectory:

\[
\frac{dx_t}{dt}=v_\theta(x_t,t,C)
\]

Inference = integrate a learned vector field.

Euler discretization:

\[
x_{n+1}=x_n+\Delta t\,v_\theta(x_n,t_n,C)
\]

Heun uses prediction + correction and has lower local error.

### Insight

“Denoising” remains a useful metaphor, but flow-based models are better understood as **transporting a sample along a vector field**.

---

# PART III — BACKBONES

## 6. U-Net

Classic diffusion-image backbone:

- multiscale convolutions;
- down/up paths;
- skip connections;
- cross-attention for conditioning.

Still relevant for SD1.x/SDXL and derivatives.

---

## 7. DiT — Diffusion Transformer

Latents are patchified:

\[
Z\rightarrow tokens\in\mathbb{R}^{N\times d}
\]

The Transformer processes those tokens with attention/MLPs.

### MMDiT / multimodal variants

Text and image/latent representations may have separate streams/weights and interact through joint attention.

Stable Diffusion 3 is a landmark of this transition: rectified flow + multimodal diffusion Transformer.

Qwen-Image-2.0 exemplifies modern unified generation+editing in 2026.

---

# PART IV — CONDITIONING

## 8. Prompt embedding

\[
C_{text}=Encoder(prompt)
\]

The prompt does not push pixels directly; it changes activations, attention, and/or modulation inside the model operator.

### Order/weighting

Depends on:

- tokenizer;
- encoder;
- frontend prompt parser;
- training recipe.

Syntax such as `(word:1.5)` is a **pipeline/UI convention**, not a universal law.

---

## 9. Negative conditioning

Classic CFG:

\[
f_c=f_\theta(x_t,t,C_{pos})
\]

\[
f_u=f_\theta(x_t,t,C_{neg/uncond})
\]

\[
f_g=f_u+s(f_c-f_u)
\]

The “negative prompt” is therefore an alternative condition used to construct \(f_u\), not a universal magical repulsion vector.

---

## 10. Reference/image conditioning

May enter as:

- encoded latent;
- cross-attention reference;
- vision embedding;
- ControlNet-like residual;
- adapter;
- masked latent/inpainting state.

There is no single universal “img2img mechanism.”

---

# PART V — GUIDANCE

## 11. Classifier-Free Guidance

\[
f_g=f_u+s(f_c-f_u)
\]

### Geometric interpretation

\[
\Delta f=f_c-f_u
\]

CFG amplifies displacement in the differential direction induced by conditioning.

### Failure surface

In general:

\[
Alignment(s)\uparrow
\]

up to a certain regime, while quality/diversity may decline under excessive guidance.

There is no universal “7 is the standard.”

---

## 12. Guidance rescale and modern guiders

Modern methods may:

- limit overexposure;
- apply guidance only over a subset of steps;
- perturb specific layers;
- combine multiple guiders.

So “CFG Scale” is now just one member of the broader family of **guidance operators**.

---

# PART VI — SCHEDULE ≠ SOLVER

## 13. Schedule

Defines evaluation points:

\[
t_0>t_1>\cdots>t_N
\]

or:

\[
\sigma_0>\sigma_1>\cdots>\sigma_N
\]

This is the **discretization grid**.

Conceptual examples:

- linear;
- cosine;
- Karras-like sigma spacing;
- flow-specific schedules;
- shifted schedules.

---

## 14. Solver / sampler

Defines the integration rule:

\[
x_{n+1}=\Phi(x_n,f_\theta,t_n,t_{n+1})
\]

### Euler

First order.

### Heun

Predictor-corrector.

### Multistep/DPM families

Use multiple evaluations or previous states to achieve higher order/efficiency.

### Rule

\[
\boxed{Scheduler\neq Sampler/Solver}
\]

They may appear side by side in ComfyUI, but they are conceptually different objects.

---

## 15. Steps and NFE

`Steps` is the number of discretization steps. Actual cost depends on network evaluations:

\[
NFE=\text{number of }f_\theta\text{ forward passes}
\]

A method with two evaluations per step may cost roughly 2× the denoiser work of a one-evaluation method.

### Quality

\[
Q(N)\not\text{ is monotonically increasing for every model}
\]

Distilled/few-step models operate at a different optimum.

---

# PART VII — IMG2IMG / INPAINT

## 16. Denoising strength as an entry point on the trajectory

An image is encoded:

\[
z_0=E(image)
\]

Noise is added up to some level \(t_s\):

\[
z_{t_s}=\alpha_{t_s}z_0+\sigma_{t_s}\epsilon
\]

The reverse process then begins there.

Denoising strength is therefore better understood as **how much of the original trajectory is discarded**, not simply “creativity.”

### Intuitive approximation

- low: preserves structure;
- high: increases structural freedom;
- 1.0: approaches generation from noise, depending on the pipeline.

---

## 17. Inpainting

Mask \(M\):

\[
x_t'=M\odot x_t^{generated}+(1-M)\odot x_t^{reference}
\]

Implementations may incorporate the mask/latent in more sophisticated ways, but the core idea is to constrain degrees of freedom spatially.

---

# PART VIII — RESOLUTION

## 18. Native training regime

“Native resolution” is a training distribution, not necessarily a single number.

Generating outside that regime can alter composition, object scale, and stability.

### Modern rule

Do not use the old law “never generate 2048 directly.” Ask:

1. which buckets/resolutions was the model trained on?
2. what is the cost of the latent token count?
3. does the autoencoder support the resolution?
4. does the positional encoding extrapolate?

---

## 19. Hires/upscale

Hires fix is a **pipeline strategy**, not a fundamental parameter.

Flow:

\[
low/medium\ res\ generation\rightarrow upscale\rightarrow img2img/refine
\]

It is useful when the model composes better at lower resolution or when quadratic attention cost makes native high-resolution generation expensive.

---

# PART IX — SEED AND REPRODUCTION

## 20. Seed

The seed usually initializes noise:

\[
x_T\sim\mathcal N(0,I;seed)
\]

But output also depends on:

\[
R=f(weights,VAE,text\ encoder,prompt,schedule,solver,steps,guidance,dtype,kernel,backend)
\]

Same seed with a different pipeline ≠ same image.

---

# PART X — MEMORY/COMPUTE

## 21. Latent token count

If latent \(H_l\times W_l\) is patchified with \(p_h\times p_w\):

\[
N=\frac{H_lW_l}{p_hp_w}
\]

Full attention:

\[
O(N^2d)
\]

Doubling both H and W quadruples token count and may multiply the quadratic attention component by ~16× before optimizations.

---

## 22. CFG and cost

Classic CFG may require two predictions:

\[
f_c,\ f_u
\]

Without special batching/fusion:

\[
Cost_{CFG}\approx2\times Cost_{conditional\ pass}
\]

Additional guiders may add extra forward passes.

---

# PART XI — COUPLING MATRIX

| Control ↑ | Prompt adherence | Diversity | Compute | Reference structure |
|---|---:|---:|---:|---:|
| CFG | ↑ until saturation | ↓ | ↑ if extra pass | — |
| Steps/NFE | may ↑ until plateau | ~ | ↑ | — |
| Denoise strength | conditioning may dominate | ↑ | depends | ↓ |
| Resolution | potential detail ↑ | — | ↑ sharply | — |
| Guidance rescale | stabilizes high-CFG | may ↑ | small | — |
| Reference weight | ↑ reference adherence | ↓ | varies | ↑ |

---

# PART XII — COMFYUI MAPPING

## 23. What each node represents

| Concept | ComfyUI |
|---|---|
| \(f_\theta\) | model/UNet/DiT loader |
| \(C\) | text/image encoders + conditioning nodes |
| initial state | Empty Latent / encoded image / noise |
| solver | sampler selection |
| schedule | scheduler/sigmas |
| guidance | CFG/guider nodes |
| integration loop | KSampler/advanced sampler |
| decoder | VAE Decode |

The advantage of ComfyUI is precisely that it exposes the graph that simpler GUIs hide.

---

# PART XIII — DIAGNOSTICS

## 24. Symptom → layer

| Symptom | Investigate |
|---|---|
| poor composition | model/training resolution/conditioning |
| prompt ignored | text encoding/guidance/model capability |
| oversaturation | guidance/schedule/VAE |
| bad hands | model prior/conditioning/control/refine |
| img2img changes too much | denoise entry point |
| OOM | latent size/attention/activations/model residency |
| same seed differs | backend/dtype/solver/pipeline mismatch |

---

## 25. Snapshot 2026

- Stable Diffusion 3: modern reference for rectified flow + MMDiT.
- Qwen-Image-2.0: unified generation and editing in a multimodal framework.
- Diffusers/ComfyUI ecosystem: guidance is no longer just one CFG scalar and may include multiple operators and temporal windows.

## References

- Stable Diffusion 3 — https://arxiv.org/abs/2403.03206
- Qwen-Image-2.0 — https://arxiv.org/abs/2605.10730
- Diffusers guiders — https://huggingface.co/docs/diffusers/main/api/modular_diffusers/guiders
