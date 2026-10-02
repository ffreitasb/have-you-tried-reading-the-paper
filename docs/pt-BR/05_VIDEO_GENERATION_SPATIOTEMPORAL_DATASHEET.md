---
title: Video Generation — Spatiotemporal Latent Datasheet v2.0
tags: [ai, video, diffusion, flow, temporal, dit]
updated: 2026-10-01
---

# Video Generation — Spatiotemporal Latent Datasheet v2.0

> Vídeo não é “imagem + motion slider”. É geração sobre um estado espaço-temporal comprimido, onde identidade, geometria, câmera, movimento e eventualmente áudio precisam permanecer coerentes através de $`T`$.

## 1. Tensor fundamental

Pixels:

```math
X\in\mathbb{R}^{B\times T\times H\times W\times C}
```

Após codec/VAE espaço-temporal:

```math
Z\in\mathbb{R}^{B\times T_l\times H_l\times W_l\times C_l}
```

---

## 2. Compressão espacial e temporal

Defina:

```math
r_s=\frac{H}{H_l}=\frac{W}{W_l}
```

```math
r_t=\frac{T}{T_l}
```

Quanto maior a compressão, menor o custo do denoiser/DiT, mas maior a carga colocada no decoder para reconstruir detalhes/movimento.

### Insight

A resolução observável `1920×1080×N frames` não é a dimensão diretamente processada pelo core model; o custo depende do **latent token count**.

---

## 3. Patchification

Se o latent é patchificado:

```math
N=T_pH_pW_p
```

Atenção global ingênua:

```math
O(N^2)
```

Por isso vídeo exige:

- temporal compression;
- factorized attention;
- windowing;
- sparse attention;
- FlashAttention;
- sequence parallelism.

---

# PARTE I — GENERATION TOPOLOGY

## 4. Full-sequence generation

Todos os frames/latentes fazem parte do mesmo estado:

```math
Z_t=[z_t^1,z_t^2,\ldots,z_t^T]
```

O modelo pode denoise/transportar a sequência conjuntamente.

### Consequência

Não existe lei matemática “último frame sempre é pior”.

---

## 5. Causal/chunked/continuation generation

Quando blocos futuros dependem explicitamente de outputs anteriores:

```math
Z_{chunk,k+1}\sim p(Z\mid Z_{chunk,\le k},C)
```

erros podem acumular:

```math
e_{k+1}=f(e_k,\ldots)
```

Aqui drift temporal acumulado é uma preocupação estrutural real.

---

# PARTE II — MOTION E COHERENCE

## 6. Motion não é uma variável universal

`motion_bucket_id`/`motion score` existem em famílias específicas. O conceito físico universal é **magnitude/complexidade da transformação temporal** exigida pelo conditioning.

Quanto maior:

- deslocamento;
- deformação;
- oclusão/desoclusão;
- mudança de viewpoint;
- interação multiobjeto;

maior a dificuldade de manter correspondência temporal.

### Heurística, não lei

```math
Motion\ complexity\uparrow\Rightarrow Coherence\ risk\uparrow
```

mas a força da relação depende da arquitetura e do treino.

---

## 7. Optical-flow mental model

Para um ponto/feature:

```math
(x_t,y_t)\rightarrow(x_{t+1},y_{t+1})
```

O modelo precisa inferir simultaneamente:

- correspondence;
- visibility;
- deformation;
- appearance consistency;
- new content em áreas desocluídas.

“Melting” é falha de identidade/correspondence, não simplesmente “noise demais”.

---

# PARTE III — CONDITIONING

## 8. Text-to-video

```math
C=C_{text}
```

### Image-to-video

```math
C=\{C_{text},C_{image}\}
```

### Start/end/keyframe conditioning

```math
C=\{frame_{start},frame_{end},keyframes,\ldots\}
```

### Camera conditioning

Pode ser:

- texto;
- trajectory embedding;
- pose matrices;
- flow/depth/control representation.

“Pan/zoom” como botão é UI/pipeline; camera trajectory é o conceito geral.

---

## 9. Noise augmentation em I2V

Alguns pipelines adicionam noise à referência antes de condicionar/continuar.

Isso aumenta liberdade, mas não é universalmente parametrizado em `0..1`.

Classificar como `MODEL/PIPE`.

---

# PARTE IV — GUIDANCE

## 10. CFG em vídeo

Mesma formulação geral:

```math
f_g=f_u+s(f_c-f_u)
```

mas agora $`f`$ atua sobre tensor espaço-temporal.

Guidance alto pode intensificar prompt adherence e simultaneamente amplificar inconsistências/oversharpening/flicker dependendo do modelo.

---

## 11. Spatio-Temporal Guidance — STG

Pipelines modernos podem criar uma prediction “degradada” perturbando self-attention/blocos e afastar a trajetória dela:

```math
f_{guided}=f_{base}+s_{stg}(f_{base}-f_{perturbed})
```

A ideia é fortalecer estrutura/coerência espaço-temporal usando uma direção diferencial, análoga em espírito ao CFG mas com outra perturbação.

LTX-2.x expõe STG como controle explícito.

---

## 12. Modality Isolation Guidance

Em modelos conjuntos vídeo+áudio, uma prediction pode ser obtida com cross-modality attention desligada e usada como referência fraca:

```math
f_{guided}=f+ s_m(f-f_{isolated})
```

Isso mostra que guidance é uma família geral de **contrastes entre predictions**, não apenas prompt positivo vs negativo.

---

# PARTE V — FPS

## 13. FPS observável vs latent temporal rate

FPS é uma propriedade do output:

```math
Duration=Frames/FPS
```

Mas custo do modelo depende de $`T_l`$, não diretamente do FPS final quando há temporal compression/interpolation.

### Não confundir

- gerar 60 frames reais;
- gerar 15 frames + interpolation 4×;
- gerar latent temporally compressed e decodificar 60 frames.

São pipelines matematicamente diferentes.

---

## 14. Frame interpolation

Modelo separado pode estimar frames intermediários:

```math
I_{t+\alpha}=F(I_t,I_{t+1},\alpha)
```

Isso não aumenta a informação temporal original do generative core da mesma forma que gerar mais latent frames.

---

# PARTE VI — DURATION E WINDOWING

## 15. Duração

```math
T=FPS\cdot duration
```

Mas latent frames:

```math
T_l\approx T/r_t
```

Long videos podem usar janelas:

```math
W_1,W_2,\ldots,W_k
```

com overlap:

```math
|W_i\cap W_{i+1}|>0
```

Maior overlap aumenta continuidade e compute.

---

## 16. Drift em long-form

Possíveis causas:

- causal chunking;
- context truncation;
- reference refresh;
- accumulation de generated conditioning;
- identity representation fraca;
- shot changes.

A solução correta depende da topology, não de uma regra como “cortar o último segundo”.

---

# PARTE VII — CAMERA

## 17. Camera vs object motion

Idealmente decompor:

```math
Motion_{observed}=Motion_{camera}+Motion_{objects}+deformation
```

Promptar tudo como uma frase deixa o modelo inferir a decomposição. Control representations podem reduzir ambiguidade.

---

# PARTE VIII — COMPUTE

## 18. Token count

```math
N=T_pH_pW_p
```

Dobrar duração mantendo tudo:

```math
N\approx2N
```

Atenção global ingênua:

```math
N^2\rightarrow4N^2
```

Esse é o motivo estrutural para compressão e atenção fatorada.

---

## 19. Guidance cost

CFG + STG + modality guidance podem exigir múltiplos forwards por step.

```math
Cost\approx NFE\times passes_{guidance}\times C_{forward}
```

Um slider de guidance pode portanto alterar **qualidade e custo**.

---

# PARTE IX — COUPLING MATRIX

| Controle ↑ | Motion freedom | Temporal coherence | Compute | Identity |
|---|---:|---:|---:|---:|
| duration | — | risco ↑ | ↑ forte | risco ↓ |
| resolution | — | risco indireto | ↑ forte | potencial ↑ |
| I2V reference weight | ↓ | ↑ | varia | ↑ |
| CFG | aderência ↑ | não monotônico | ↑ | pode ↑/↓ |
| STG | — | potencial ↑ | ↑ | potencial ↑ |
| overlap | — | ↑ | ↑ | ↑ |
| interpolation | smoothness ↑ | não cria identidade | ↑ pós | ~ |

---

# PARTE X — COMFYUI

## 20. Nós a procurar conceitualmente

- video VAE/codec;
- frame/latent dimensions;
- model/DiT;
- text/reference conditioning;
- sampler/scheduler;
- CFG/STG/custom guider;
- continuation/keyframe controls;
- VAE decode;
- interpolation/upscale.

O parâmetro que parece “motion” pode estar implementando conditioning, noise augmentation, temporal schedule ou apenas prompt convention. Verificar o node/model documentation.

---

# PARTE XI — DIAGNÓSTICO

| Sintoma | Investigar |
|---|---|
| face drift | identity conditioning/windowing/model |
| flicker | temporal model/guidance/decoder |
| câmera “derrete” cena | camera conditioning + motion complexity |
| último chunk degrada | causal continuation/error accumulation |
| OOM | T×H×W latent tokens / activations |
| áudio fora de sincronia | cross-modal conditioning/guidance |

---

## 21. Snapshot 2026

LTX-2.x expõe um stack moderno de vídeo+áudio com DiT, CFG, STG e modality-isolation guidance separados por modalidade. Isso é uma boa demonstração de por que o antigo “motion score + CFG + FPS” já não descreve a máquina inteira.

## Referências

- LTX-2 Diffusers — https://huggingface.co/docs/diffusers/main/api/pipelines/ltx2
- CogVideoX — https://arxiv.org/abs/2408.06072
