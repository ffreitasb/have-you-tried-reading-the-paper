---
title: Image Generation — Diffusion, Flow & DiT Datasheet v2.0
tags: [ai, image, diffusion, rectified-flow, dit, comfyui]
updated: 2026-10-01
---

# Image Generation — Diffusion, Flow & DiT Datasheet v2.0

> A variável central não é “qual sampler deixa bonito”. É **qual estado latente está sendo percorrido, qual grandeza a rede prevê e qual integrador transforma essa previsão em trajetória**.

## 1. Grafo canônico

```math
prompt/reference\rightarrow condition\ encoder\rightarrow latent\ state\rightarrow denoiser/vector\ field\rightarrow solver\ loop\rightarrow AE/VAE\ decoder\rightarrow pixels
```

Pipeline típico:

```math
C\rightarrow x_T\rightarrow f_\theta(x_t,t,C)\rightarrow x_{t-1}\rightarrow\cdots\rightarrow x_0\rightarrow D(x_0)
```

---

# PARTE I — REPRESENTAÇÃO

## 2. Pixel space vs latent space

Pixel space:

```math
X\in\mathbb{R}^{B\times 3\times H\times W}
```

Latent space:

```math
Z=E(X)\in\mathbb{R}^{B\times C_l\times H_l\times W_l}
```

Com fator de compressão espacial $`f`$:

```math
H_l\approx H/f,\qquad W_l\approx W/f
```

A geração moderna quase sempre economiza compute trabalhando em $`Z`$, não diretamente em pixels.

### Consequência

Resolution aumenta número de latent positions:

```math
N_l\propto H_lW_l
```

Em Transformer com atenção global sobre patches:

```math
C_{attn}\sim O(N^2)
```

---

## 3. Autoencoder / VAE

Encoder:

```math
X\rightarrow Z
```

Decoder:

```math
\hat X=D(Z)
```

O decoder impõe um teto de fidelidade independente do denoiser.

### Failure modes

- reconstruction blur;
- color shift;
- high-frequency loss;
- latent scaling mismatch;
- decoder incompatibility.

“Imagem lavada” não prova automaticamente VAE errado; pode ser conditioning/guidance/decoder/range mismatch.

---

# PARTE II — PROCESSO GENERATIVO

## 4. Diffusion clássico

Forward simplificado:

```math
x_t=\alpha_t x_0+\sigma_t\epsilon,\qquad \epsilon\sim\mathcal N(0,I)
```

A rede pode prever:

- $`\epsilon`$: noise prediction;
- $`x_0`$: clean sample;
- $`v`$: velocity parametrization;
- score $`\nabla_x\log p_t(x)`$.

Essas parametrizações não são apenas nomes de UI; mudam escala numérica e comportamento do solver.

---

## 5. Rectified flow / flow matching

Trajetória contínua:

```math
\frac{dx_t}{dt}=v_\theta(x_t,t,C)
```

Inferência = integrar um campo vetorial aprendido.

Discretização Euler:

```math
x_{n+1}=x_n+\Delta t\,v_\theta(x_n,t_n,C)
```

Heun usa previsão + correção e tem erro local menor.

### Insight

“Denoising” continua uma metáfora útil, mas modelos flow-based são melhor entendidos como **transportar uma amostra ao longo de um vector field**.

---

# PARTE III — BACKBONES

## 6. U-Net

Clássico diffusion image backbone:

- convoluções multi-escala;
- down/up paths;
- skip connections;
- cross-attention para conditioning.

Ainda relevante para SD1.x/SDXL e derivados.

---

## 7. DiT — Diffusion Transformer

Latentes são patchificados:

```math
Z\rightarrow tokens\in\mathbb{R}^{N\times d}
```

O Transformer processa esses tokens com attention/MLP.

### MMDiT / multimodal variants

Texto e imagem/latente podem ter streams/weights próprios e interação via joint attention.

Stable Diffusion 3 é um marco dessa transição: rectified flow + multimodal diffusion transformer.

Qwen-Image-2.0 exemplifica geração+edição multimodal moderna em 2026.

---

# PARTE IV — CONDITIONING

## 8. Prompt embedding

```math
C_{text}=Encoder(prompt)
```

O prompt não empurra diretamente pixels; modifica activations/attention/modulation do model operator.

### Ordem/weighting

Dependem de:

- tokenizer;
- encoder;
- prompt parser do frontend;
- training recipe.

Sintaxe `(word:1.5)` é uma **convenção de pipeline/UI**, não lei universal.

---

## 9. Negative conditioning

CFG clássico:

```math
f_c=f_\theta(x_t,t,C_{pos})
```

```math
f_u=f_\theta(x_t,t,C_{neg/uncond})
```

```math
f_g=f_u+s(f_c-f_u)
```

O “negative prompt” é portanto uma condição alternativa usada para construir $`f_u`$, não um vetor mágico de repulsão universal.

---

## 10. Reference/image conditioning

Pode entrar como:

- encoded latent;
- cross-attention reference;
- vision embedding;
- ControlNet-like residual;
- adapter;
- masked latent/inpainting state.

Não existe um único “img2img mechanism”.

---

# PARTE V — GUIDANCE

## 11. Classifier-Free Guidance

```math
f_g=f_u+s(f_c-f_u)
```

### Interpretação geométrica

```math
\Delta f=f_c-f_u
```

CFG aumenta o deslocamento na direção diferencial induzida pelo conditioning.

### Failure surface

Em geral:

```math
Alignment(s)\uparrow
```

até certo regime, enquanto qualidade/diversidade podem cair com guidance excessivo.

Não existe “7 é o padrão universal”.

---

## 12. Guidance rescale e guiders modernos

Métodos modernos podem:

- limitar overexposure;
- aplicar guidance somente em uma faixa de steps;
- perturbar camadas;
- combinar múltiplos guiders.

Portanto “CFG Scale” virou apenas um membro da família **guidance operators**.

---

# PARTE VI — SCHEDULE ≠ SOLVER

## 13. Schedule

Define pontos de avaliação:

```math
t_0>t_1>\cdots>t_N
```

ou:

```math
\sigma_0>\sigma_1>\cdots>\sigma_N
```

É a **malha de discretização**.

Exemplos conceituais:

- linear;
- cosine;
- Karras-like sigma spacing;
- flow-specific schedules;
- shifted schedules.

---

## 14. Solver / sampler

Define a regra de integração:

```math
x_{n+1}=\Phi(x_n,f_\theta,t_n,t_{n+1})
```

### Euler

Primeira ordem.

### Heun

Preditor-corretor.

### Multistep/DPM families

Usam múltiplas avaliações/estados anteriores para maior ordem/eficiência.

### Regra

```math
\boxed{Scheduler\neq Sampler/Solver}
```

No ComfyUI podem aparecer próximos, mas são objetos conceitualmente diferentes.

---

## 15. Steps e NFE

`Steps` é número de passos da malha. Custo real depende de avaliações da rede:

```math
NFE=\text{number of }f_\theta\text{ forward passes}
```

Um método com duas avaliações/step pode custar aproximadamente 2× o denoiser de um método com uma.

### Qualidade

```math
Q(N)\not\text{ é monotonicamente crescente em todos os modelos}
```

Modelos distilled/few-step possuem outro ponto de operação.

---

# PARTE VII — IMG2IMG / INPAINT

## 16. Denoising strength como ponto de entrada na trajetória

Uma imagem é codificada:

```math
z_0=E(image)
```

Noise é adicionado até um nível $`t_s`$:

```math
z_{t_s}=\alpha_{t_s}z_0+\sigma_{t_s}\epsilon
```

Então o processo reverso começa dali.

Denoising strength é portanto melhor entendido como **quanto da trajetória original é descartada**, não simplesmente “criatividade”.

### Aproximação intuitiva

- baixo: preserva estrutura;
- alto: amplia liberdade estrutural;
- 1.0: aproxima geração a partir de noise conforme pipeline.

---

## 17. Inpainting

Máscara $`M`$:

```math
x_t'=M\odot x_t^{generated}+(1-M)\odot x_t^{reference}
```

Implementações podem incorporar máscara/latente de formas mais sofisticadas, mas a ideia fundamental é restringir graus de liberdade espacialmente.

---

# PARTE VIII — RESOLUÇÃO

## 18. Native training regime

“Resolução nativa” é uma distribuição de treino, não necessariamente um número único.

Gerar fora do regime pode alterar composição, escala de objetos e estabilidade.

### Regra moderna

Não usar a antiga lei “nunca gere 2048 direto”. Perguntar:

1. em quais buckets/resoluções o modelo foi treinado?
2. qual o custo do latent token count?
3. o autoencoder suporta a resolução?
4. o positional encoding extrapola?

---

## 19. Hires/upscale

Hires fix é uma **estratégia de pipeline**, não um parâmetro fundamental.

Fluxo:

```math
low/medium\ res\ generation\rightarrow upscale\rightarrow img2img/refine
```

É útil quando o modelo compõe melhor em menor resolução ou quando o custo quadrático torna geração nativa cara.

---

# PARTE IX — SEED E REPRODUÇÃO

## 20. Seed

Seed normalmente inicializa noise:

```math
x_T\sim\mathcal N(0,I;seed)
```

Mas output depende também de:

```math
R=f(weights,VAE,text\ encoder,prompt,schedule,solver,steps,guidance,dtype,kernel,backend)
```

Mesma seed com pipeline diferente ≠ mesma imagem.

---

# PARTE X — MEMORY/COMPUTE

## 21. Latent token count

Se latent $`H_l\times W_l`$ é patchificado por $`p_h\times p_w`$:

```math
N=\frac{H_lW_l}{p_hp_w}
```

Attention full:

```math
O(N^2d)
```

Dobrar H e W quadruplica tokens e pode multiplicar o componente quadrático de attention em ~16×, antes das otimizações.

---

## 22. CFG e custo

CFG clássico pode exigir duas predictions:

```math
f_c,\ f_u
```

Se não houver batching/fusão especial:

```math
Cost_{CFG}\approx2\times Cost_{conditional\ pass}
```

Guiders adicionais podem adicionar forwards extras.

---

# PARTE XI — COUPLING MATRIX

| Controle ↑ | Prompt adherence | Diversity | Compute | Estrutura da referência |
|---|---:|---:|---:|---:|
| CFG | ↑ até saturar | ↓ | ↑ se extra pass | — |
| Steps/NFE | pode ↑ até plateau | ~ | ↑ | — |
| Denoise strength | condicionamento pode dominar | ↑ | depende | ↓ |
| Resolution | detalhe potencial ↑ | — | ↑ forte | — |
| Guidance rescale | estabiliza high-CFG | pode ↑ | pequeno | — |
| Reference weight | ↑ ref adherence | ↓ | varia | ↑ |

---

# PARTE XII — COMFYUI MAPPING

## 23. O que cada node representa

| Conceito | ComfyUI |
|---|---|
| $`f_\theta`$ | model/UNet/DiT loader |
| $`C`$ | text/image encoders + conditioning nodes |
| initial state | Empty Latent / encoded image / noise |
| solver | sampler selection |
| schedule | scheduler/sigmas |
| guidance | CFG/guider nodes |
| integration loop | KSampler/advanced sampler |
| decoder | VAE Decode |

A vantagem do ComfyUI é justamente expor explicitamente o grafo que GUIs simples escondem.

---

# PARTE XIII — DIAGNÓSTICO

## 24. Sintoma → camada

| Sintoma | Investigar |
|---|---|
| composição ruim | model/training resolution/conditioning |
| prompt ignorado | text encoding/guidance/model capability |
| oversaturation | guidance/schedule/VAE |
| mãos ruins | model prior/conditioning/control/refine |
| imagem muda demais em img2img | denoise entry point |
| OOM | latent size/attention/activations/model residency |
| mesma seed difere | backend/dtype/solver/pipeline mismatch |

---

## 25. Snapshot 2026

- Stable Diffusion 3: referência moderna de rectified flow + MMDiT.
- Qwen-Image-2.0: geração e edição unificadas em framework multimodal.
- Ecossistema Diffusers/ComfyUI: guidance deixou de ser apenas um scalar CFG e pode incluir múltiplos operadores e janelas temporais.

## Referências

- Stable Diffusion 3 — https://arxiv.org/abs/2403.03206
- Qwen-Image-2.0 — https://arxiv.org/abs/2605.10730
- Diffusers guiders — https://huggingface.co/docs/diffusers/main/api/modular_diffusers/guiders
