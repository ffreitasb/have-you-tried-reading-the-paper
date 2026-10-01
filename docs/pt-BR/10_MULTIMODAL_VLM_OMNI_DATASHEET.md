---
title: Multimodal / VLM / Omni Model Datasheet v1.0
tags: [ai, multimodal, vlm, omni, vision-language, audio-language, inference]
updated: 2026-10-01
---

# Multimodal / VLM / Omni Model Datasheet v1.0

> Multimodalidade não é “um LLM que aceita imagem”. É a engenharia de **converter sinais com topologias, resoluções e relógios incompatíveis em estados que possam interagir dentro do mesmo sistema**.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 1. O problema fundamental

Considere modalidades:

\[
X=\{X_t,X_v,X_a,X_{vid}\}
\]

com:

- texto: sequência discreta;
- imagem: grade 2D;
- áudio: waveform / espectrograma / codec sequence;
- vídeo: grade 2D + tempo.

O sistema precisa construir representações compatíveis:

\[
Z_m=E_m(X_m)
\]

seguido por alguma fusão:

\[
H=\mathcal F(Z_t,Z_v,Z_a,Z_{vid})
\]

A pergunta-chave não é “qual prompt usar?”, mas:

\[
\boxed{Como\ cada\ modalidade\ vira\ estado\ compartilhável?}
\]

---

# 2. Topologias multimodais

## 2.1 Encoder + projector + LLM

Forma VLM clássica:

\[
Image\xrightarrow{VisionEncoder}Z_v
\xrightarrow{Projector}Z'_v
\rightarrow LLM
\]

Se:

\[
Z_v\in\mathbb R^{N_v\times d_v}
\]

mas o backbone usa hidden size \(d_h\):

\[
Z'_v=Z_vW_p,
\quad
W_p\in\mathbb R^{d_v\times d_h}
\]

O projector pode ser:

- linear;
- MLP;
- convolutional/downsampler;
- resampler com queries aprendidas;
- attention bridge.

### Failure surface

Backbone enorme + bridge fraco ainda produz gargalo:

\[
Information(X_v)\gg Information(Z'_v)
\]

A perda já ocorreu antes do LLM.

---

## 2.2 Cross-attention bridge

Texto consulta features visuais/sonoras:

\[
Q=H_{text}W_Q
\]

\[
K=Z_vW_K,\quad V=Z_vW_V
\]

\[
A=softmax\left(\frac{QK^T}{\sqrt d}\right)V
\]

Vantagem: não é necessário serializar toda modalidade como “tokens textuais” equivalentes.

Trade-off: mais módulos, estado e custo de atenção cruzada.

---

## 2.3 Joint / early fusion

Todas as modalidades entram numa sequência/estado conjunto:

\[
H_0=[Z_t;Z_v;Z_a;Z_{vid}]
\]

O backbone aprende interações diretamente.

### Custo

Se atenção global for usada:

\[
N_{total}=N_t+N_v+N_a+N_{vid}
\]

\[
C_{attn}\sim O(N_{total}^2)
\]

Logo, cada modalidade compete por orçamento de contexto.

---

## 2.4 Late fusion

Cada modalidade é processada mais profundamente antes da combinação:

\[
H=Fuse(f_t(X_t),f_v(X_v),f_a(X_a))
\]

Prós:

- especialização;
- menor interferência inicial.

Contras:

- alinhamento entre representações pode ser mais difícil;
- interação cross-modal tardia.

---

## 2.5 Omni / Thinker–Talker style

Sistemas omni podem separar:

\[
Perception/Reasoning\rightarrow Thinker
\]

\[
Speech/Audio\ Generation\rightarrow Talker
\]

mas compartilhar contexto/representações.

A saída pode ser interleaved:

\[
Text\ tokens + Speech\ codec\ tokens
\]

ou multi-head.

---

# 3. Vision tokenization

## 3.1 Patchification

Imagem:

\[
X\in\mathbb R^{H\times W\times C}
\]

Patch \(P_h\times P_w\):

\[
N_v\approx
\frac{H}{P_h}\frac{W}{P_w}
\]

Exemplo idealizado 1024², patch 16:

\[
N_v=64^2=4096
\]

antes de pooling/merging.

Isso explica por que “uma imagem” pode consumir milhares de posições internas.

---

## 3.2 Dynamic resolution

Em vez de resize fixo, sistemas modernos podem adaptar número de patches à razão de aspecto/resolução.

Estado:

\[
N_v=f(H,W,P,budget)
\]

### Consequência

Duas imagens distintas podem ter custo de contexto muito diferente mesmo sendo ambas “1 imagem”.

---

## 3.3 Patch merging / token compression

Agrupamento \(k\times k\):

\[
N'_v\approx\frac{N_v}{k^2}
\]

Trade-off:

\[
TokenBudget\downarrow
\leftrightarrow
SpatialDetail\downarrow
\]

Não existe compressão gratuita.

---

# 4. Vídeo dentro de um VLM

Sem compressão:

\[
N_{vid}\approx
T_f\frac{H}{P_h}\frac{W}{P_w}
\]

onde \(T_f\) é o número de frames amostrados.

Mesmo 1 fps pode produzir enorme sequence length em vídeo longo.

## Estratégias

- frame subsampling;
- temporal pooling;
- tubelets;
- temporal patchification;
- hierarchical summarization;
- memory/compression tokens;
- long-context sparse attention.

### Regra

\[
VideoDuration\uparrow
\not\Rightarrow
FramesProcessed\uparrow\ linearmente
\]

porque pipelines podem mudar sampling rate ou comprimir adaptativamente.

---

# 5. Áudio dentro de modelos multimodais

Possíveis representações:

- log-Mel frames;
- continuous encoder states;
- semantic audio tokens;
- codec tokens;
- compressed summary tokens.

Se frontend gera \(r_a\) estados/s:

\[
N_a=r_aD
\]

para duração \(D\).

Long-form audio é portanto um problema de **sequence compression**, não apenas de janela temporal.

Veja [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

---

# 6. Positional systems multimodais

Texto tem posição 1D:

\[
p_t=t
\]

Imagem possui:

\[
p_v=(x,y)
\]

Vídeo:

\[
p_{vid}=(t,x,y)
\]

Áudio:

\[
p_a=t_{physical}
\]

Modelos multimodais precisam codificar uma relação:

\[
R(position_i,position_j)
\]

que preserve a estrutura relevante.

## Modalidade ≠ posição

Além da posição, o backbone frequentemente precisa saber **de qual modalidade veio o token**:

\[
h_i=e_i+p_i+m_i
\]

ou via modulation/segment embeddings.

---

# 7. Time alignment

Em diálogo audiovisual:

\[
Audio(t)\leftrightarrow Video(t)
\]

Uma palavra falada deve alinhar com o movimento/objeto correspondente.

Problemas:

- clocks diferentes;
- frame rates diferentes;
- codec delay;
- resampling;
- chunk boundaries.

Um sistema omni precisa estabelecer algum mapa temporal comum:

\[
\tau_m(i)\rightarrow t_{global}
\]

### Failure surface

Se alinhamento temporal falha, o modelo pode identificar corretamente **o que** ocorreu, mas associar ao frame/evento errado.

---

# 8. Spatial grounding

Compreensão visual genérica:

\[
Image\rightarrow semantics
\]

Grounding exige:

\[
Text\ phrase\rightarrow region/bbox/point
\]

Bounding box:

\[
b=(x_{min},y_{min},x_{max},y_{max})
\]

Pode ser representada como:

- tokens discretizados;
- coordenadas contínuas;
- special location vocabulary;
- segmentation masks.

A capacidade de “ver” e a capacidade de **localizar** não são equivalentes.

---

# 9. Interleaved multimodality

Em sequências mistas:

```text
[text] [image] [text] [image] [audio] [text]
```

a ordem contextual passa a carregar semântica.

O modelo precisa manter relações como:

\[
reference("segunda\ imagem")\rightarrow Z_{v,2}
\]

Esse problema combina:

- multimodal positional identity;
- long-context reference tracking;
- modality boundaries.

---

# 10. Multimodal output

## Text output

\[
H\rightarrow LMHead\rightarrow tokens
\]

## Speech output

\[
H\rightarrow SpeechHead/Talker\rightarrow codec/latent\rightarrow waveform
\]

## Image/video output

Pode haver outro backbone generativo condicionado pelo modelo de entendimento:

\[
H_{reasoning}\rightarrow C_{generator}\rightarrow Diffusion/Flow
\]

“Um modelo multimodal” pode portanto ser **um sistema de múltiplos operadores**, não uma única rede monolítica.

---

# 11. Multimodal token accounting

Para runtime:

\[
T_{effective}
=
T_{text}
+N_v
+N_a
+N_{vid}
+N_{special}
\]

Se o backbone causal constrói KV para tudo:

\[
M_{KV}\propto T_{effective}
\]

Essa equação é uma das mais úteis na prática.

### Tradução

Adicionar uma imagem pode custar mais memória/contexto que milhares de palavras.

---

# 12. Cross-modal attention cost

Se texto \(N_t\) consulta visão \(N_v\):

\[
C_{cross}\sim O(N_tN_vd)
\]

Se fundimos tudo e fazemos self-attention global:

\[
C_{joint}\sim O((N_t+N_v)^2d)
\]

A arquitetura define a curva física.

---

# 13. Training objectives multimodais

Possíveis componentes:

### Contrastive

\[
L_{contrastive}
\]

alinha representações.

### Caption/next-token

\[
L_{LM}
\]

ensina descrição/resposta.

### Reconstruction/generation

\[
L_{gen}
\]

### Grounding

\[
L_{ground}
\]

### Audio-visual synchronization

\[
L_{sync}
\]

Treino multimodal moderno pode combinar:

\[
L=\sum_i\lambda_iL_i
\]

Logo “é um VLM” não revela sua função-objetivo real.

---

# 14. Failure surfaces

## 14.1 Modality dominance

Uma modalidade sobrepõe as demais.

Ex.: modelo responde pelo prior textual mesmo quando imagem contradiz texto.

## 14.2 Projector bottleneck

Detalhes desaparecem no bridge.

## 14.3 Token starvation

Compressão agressiva perde pequenos objetos/texto visual.

## 14.4 Token explosion

Alta resolução/vídeo consome contexto e memória.

## 14.5 Temporal desynchronization

Áudio/vídeo semanticamente corretos, temporalmente errados.

## 14.6 Hallucinated grounding

Semântica plausível sem evidência espacial real.

## 14.7 Cross-modal conflict

\[
C_{text}\neq C_{vision}
\]

O modelo precisa arbitrar fontes contraditórias.

---

# 15. Controls vs observables

| Variável | Classe | Efeito |
|---|---|---|
| image resolution | `PIPE/INF` | altera visual token budget |
| frame sampling rate | `PIPE/INF` | altera temporal coverage e tokens |
| max pixels / token budget | `PIPE/BACKEND` | limita custo |
| audio chunk length | `PIPE/INF` | latência ↔ contexto acústico |
| projector type | `ARCH` | capacidade do bridge |
| vision encoder size | `ARCH/MODEL` | qualidade/custo perceptual |
| context length | `MODEL/BACKEND` | teto de estado conjunto |
| modality dropout | `OBJ/TRAIN` | robustez a modalidades ausentes |

Observáveis úteis:

- tokens por imagem/frame/s;
- context occupancy;
- grounding accuracy;
- OCR accuracy;
- audio/video alignment error;
- first-token / first-audio latency;
- VRAM peak com/sem encoder carregado.

---

# 16. Snapshot SOTA — 2026-10-01

Qwen3.5-Omni exemplifica a convergência para omni models com:

- texto, visão, áudio e vídeo;
- Thinker/Talker;
- MoE híbrido;
- contexto longo;
- streaming speech;
- sincronização audiovisual explícita.

Qwen3-Omni já havia mostrado Thinker–Talker MoE e geração de fala por codec tokens; a geração seguinte amplia escala/contexto e sincronização.

O ponto arquitetural importante não é a marca: **omni models estão tornando modality alignment + token compression + streaming state problemas tão centrais quanto o Transformer principal**.

---

# 17. Checklist para dissecar qualquer VLM/Omni

1. Qual encoder existe para cada modalidade?
2. Qual a taxa de tokens/states produzida?
3. Há projector, resampler ou joint backbone?
4. Qual hidden dimension recebe cada modalidade?
5. Como posição espacial/temporal é codificada?
6. Quantos tokens uma imagem/vídeo/segundo de áudio consome?
7. O backbone vê todas as modalidades no mesmo self-attention?
8. Há cross-attention separado?
9. Há heads/talkers/decoders independentes?
10. Qual estado persiste em streaming?
11. Como conflito entre modalidades é resolvido?
12. Qual é a curva de VRAM com resolution/duration?

---

# Referências snapshot

- Qwen3.5-Omni Technical Report — https://arxiv.org/abs/2604.15804
- Qwen3-Omni Technical Report — https://arxiv.org/abs/2509.17765
- Qwen3-ASR Technical Report — https://arxiv.org/abs/2601.21337
