---
title: Audio, Speech, Music & TTS Model Datasheet v3.0
tags: [ai, audio, speech, music, tts, asr, codec, diffusion, streaming]
updated: 2026-10-01
---

# Audio, Speech, Music & TTS Model Datasheet v3.0

> Áudio generativo não é uma única família. A variável decisiva é **como a onda foi comprimida/representada antes da geração**.

## 1. Três grandes pipelines

### A. Codec-token autoregression

```math
waveform\rightarrow codec\ tokens\rightarrow LM\rightarrow codec\ decoder\rightarrow waveform
```

### B. Latent diffusion/flow

```math
waveform\rightarrow AE\ latent\rightarrow diffusion/flow\rightarrow decoder\rightarrow waveform
```

### C. TTS/voice systems

```math
text+speaker/style\rightarrow linguistic/acoustic\ representation\rightarrow acoustic\ decoder/vocoder
```

Voice conversion adiciona outra classe:

```math
source\ speech\rightarrow content/prosody\rightarrow target\ timbre
```

Não confundir TTS com VC.

---

# PARTE I — REPRESENTAÇÃO

## 2. Waveform

```math
x\in\mathbb{R}^{channels\times samples}
```

Para sample rate $`f_s`$ e duração $`D`$:

```math
N_{samples}=f_sD
```

44.1 kHz stereo por 60 s:

```math
44,100\cdot60\cdot2\approx5.29\text{ milhões de samples}
```

Gerar diretamente nesse comprimento é caro; por isso codecs/autoencoders comprimem o tempo.

---

## 3. Codec tokens

Frame rate do codec:

```math
r_c=\frac{frames}{second}
```

Com $`K`$ codebooks:

```math
tokens/sec\approx r_cK
```

Duração:

```math
T_{tokens}\approx D\,r_cK
```

Isso liga diretamente duração a sequence length.

---

## 4. Semantic vs acoustic tokens

Um codec pode priorizar:

- conteúdo semântico;
- timbre/prosódia;
- reconstrução acústica detalhada;
- baixa bitrate/streaming.

Múltiplos codebooks podem decompor informação em camadas discretas.

Qwen3-TTS em 2026 exemplifica dois regimes: tokenizer 25 Hz single-codebook com foco semântico e tokenizer 12.5 Hz multi-codebook para bitrate/latência muito baixos.

---

## 5. Continuous audio latents

Autoencoder:

```math
Z=E(x),\qquad \hat x=D(Z)
```

Latent rate:

```math
r_l=\frac{N_{latent\ frames}}{D}
```

Stable Audio 3 usa um semantic-acoustic autoencoder para reduzir fortemente o comprimento antes da geração.

---

# PARTE II — MUSIC/AUDIO AUTOREGRESSIVE

## 6. Próximo token de áudio

```math
p(a_{1:T})=\prod_tp(a_t\mid a_{<t},C)
```

Aplicam-se:

- temperature;
- top-k/top-p;
- repetition behavior;
- KV/context limits.

### Caveat

Top-K não “corta frequências”. Ele corta **tokens discretos do codec/vocabulário**.

---

## 7. Duration

Para autoregressive codec:

```math
Compute\propto T_{tokens}
```

KV/cache também cresce com sequence length se a arquitetura for Transformer causal convencional.

---

# PARTE III — LATENT DIFFUSION/FLOW

## 8. Diffusion

```math
z_t=\alpha_tz_0+\sigma_t\epsilon
```

Rede prevê noise/velocity/clean latent.

### Flow

```math
\frac{dz_t}{dt}=v_\theta(z_t,t,C)
```

Mesmos conceitos de:

- steps;
- schedule;
- solver;
- CFG;
- seed.

Mas agora o eixo espacial é tempo/feature channels.

---

## 9. Variable-length generation

Modelos modernos podem evitar gerar sempre uma janela fixa máxima.

Custo depende do comprimento latente:

```math
N_l\propto duration
```

Se houver attention global:

```math
C_{attn}\sim O(N_l^2)
```

Logo “VRAM cresce linearmente com duração” é apenas parcialmente verdadeiro: **estado** pode crescer linearmente enquanto attention compute/activations podem crescer superlinearmente.

---

# PARTE IV — TTS

## 10. TTS decomposed

```math
Text\rightarrow semantic/linguistic\ units\rightarrow acoustic\ representation\rightarrow waveform
```

Conditioning adicional:

```math
C=\{speaker,style,language,prosody,reference\}
```

---

## 11. Speaker similarity

Não existe um knob universal chamado “Similarity Boost”. É uma abstração de determinados produtos.

O mecanismo real pode envolver:

- speaker embedding;
- reference encoder;
- prompt audio tokens;
- latent conditioning.

Aderência à voz depende da distância/compatibilidade no espaço de speaker representation, training distribution e qualidade da referência.

---

## 12. Stability

Também não é variável matemática universal. Pode mapear para:

- sampling entropy;
- style/prosody variance;
- deterministic paths;
- vendor-specific interpolation.

Classificar `Stability` como `UI` até conhecer sua implementação.

---

## 13. Prosody

Prosódia contém:

- F0/pitch;
- duration/rhythm;
- energy;
- pauses;
- emphasis.

Voice cloning de timbre e transferência de prosódia são problemas diferentes.

---

# PARTE V — SPEECH-TO-SPEECH / VOICE CONVERSION

## 14. VC

Objetivo idealizado:

```math
y=D(content(x),prosody(x),speaker_{target})
```

RVC-like systems pertencem aqui.

XTTS-like systems são primariamente TTS/voice cloning, mesmo quando usados em workflows que preservam parte de estilo via referência.

---

# PARTE VI — STREAMING

## 15. First packet latency

Para TTS interativo:

```math
Latency_{perceived}\approx T_{first\ audio\ packet}
```

Não é igual ao tempo total de síntese.

Arquiteturas causal/blockwise permitem iniciar playback antes da geração completa.

Qwen3-TTS reporta arquitetura dual-track e decoders preparados para streaming, ilustrando essa separação.

---

# PARTE VII — CONDITIONING

## 16. Text prompt

Música/SFX:

```math
C_{text}=Encoder(description)
```

### Audio prompt/reference

```math
C_{audio}=E_{ref}(waveform)
```

Pode controlar:

- melody;
- rhythm;
- timbre;
- continuation;
- structure.

O mecanismo depende do modelo; “assobiar e trocar instrumento” não é uma propriedade universal.

---

# PARTE VIII — EDITING

## 17. Audio inpainting

Mask temporal $`M`$:

```math
z'=M\odot z_{generated}+(1-M)\odot z_{reference}
```

Permite substituir intervalo mantendo contexto anterior/posterior.

### Continuation

Conditioning no prefixo:

```math
p(audio_{future}\mid audio_{past},C)
```

ou processo flow/diffusion parcialmente condicionado.

---

# PARTE IX — GUIDANCE E SAMPLING

## 18. Autoregressive

Usar sampling de tokens.

## 19. Diffusion/flow

Usar solver/schedule/guidance.

### Regra de ouro

Não misturar controles de famílias diferentes apenas porque aparecem na mesma UI.

`Top-K` só faz sentido se há distribuição discreta sendo amostrada naquele estágio.

`Steps` só faz sentido se há trajetória iterativa naquele estágio.

---

# PARTE X — QUALITY OBSERVABLES

## 20. Métricas

### Speech

- WER/CER;
- speaker similarity embedding;
- MOS/preference;
- latency;
- prosody metrics.

### Music/audio

- CLAP-like alignment;
- spectral distance;
- FAD-like metrics;
- human preference;
- structural repetition;
- beat/key consistency.

Nenhuma métrica substitui avaliação auditiva para todos os objetivos.

---

# PARTE XI — COUPLING MATRIX

| Controle ↑ | Diversity | Prompt adherence | Compute | Voice identity |
|---|---:|---:|---:|---:|
| AR temperature | ↑ | pode ↓ | ~ | pode ↓ |
| diffusion steps | ~ | pode ↑ até plateau | ↑ | — |
| CFG | ↓ | ↑ até regime útil | ↑ | depende |
| duration | — | — | ↑ | drift risk ↑ |
| reference strength | ↓ | — | varia | ↑ |
| codec bitrate | reconstruction ↑ | — | token/decoder cost ↑ | potencial ↑ |

---

# PARTE XII — FAILURE DIAGNOSTICS

| Sintoma | Investigar |
|---|---|
| voz muda ao longo do texto | speaker conditioning/context/streaming state |
| palavras erradas | linguistic model/tokenizer |
| metálico/phasey | codec/vocoder/flow guidance |
| música entra em loop | AR sampling/context/model prior |
| artefato em edição | mask boundaries/latent codec |
| muita VRAM em duração longa | latent/token length/attention |

---

## 21. Snapshot 2026

- Qwen3-TTS: dual-track LM, codecs de 25 Hz e 12.5 Hz, streaming e blockwise DiT/causal decoding conforme variante.
- Stable Audio 3: semantic-acoustic autoencoder + latent diffusion; variable-length generation, inpainting e adversarial post-training para menos inference steps.

## Referências

- Qwen3-TTS — https://arxiv.org/abs/2601.15621
- Stable Audio 3 — https://arxiv.org/abs/2605.17991

---

# PARTE XIII — AUTOMATIC SPEECH RECOGNITION (ASR)

> TTS não é simplesmente invertido para virar ASR. O problema inverso possui alinhamento latente, ruído acústico, múltiplos falantes, endpointing e uma função-objetivo diferente.

Relacionados: [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

## 22. Pipeline acústico clássico/moderno

```math
waveform
\rightarrow frontend/encoder
\rightarrow H_{speech}
\rightarrow recognition\ head/decoder
\rightarrow text
```

Frontend pode usar:

- log-Mel spectrogram;
- learned convolutional frontend;
- speech tokenizer/codec;
- pretrained speech encoder.

---

## 23. STFT

Para janela $`w[n]`$:

```math
X(m,k)=\sum_n x[n]w[n-mR]e^{-j2\pi kn/N}
```

onde $`R`$ é hop size.

A STFT cria representação tempo-frequência.

---

## 24. Mel filterbank

Frequência Hz é mapeada aproximadamente para escala perceptual Mel:

```math
m=2595\log_{10}\left(1+\frac{f}{700}\right)
```

Log-Mel:

```math
F=\log(Mel(|STFT(x)|^2)+\epsilon)
```

Muitos ASRs modernos ainda começam com algo equivalente a isso, mesmo quando backbone é Transformer/Conformer.

---

## 25. Acoustic frame rate

Se hop $`R`$ samples e sample rate $`f_s`$:

```math
r_f=\frac{f_s}{R}
```

frames/s.

Áudio de duração $`D`$:

```math
T_f\approx D\,r_f
```

Long-form speech portanto explode sequence length antes de qualquer LLM.

---

## 26. Conformer

Combina attention global/contextual com convolução local:

```math
H'
=H+\frac12FFN(H)
```

```math
H''=H'+MHSA(H')
```

```math
H'''=H''+Conv(H'')
```

```math
Y=LayerNorm(H'''+\frac12FFN(H'''))
```

A ideia: speech possui dependências globais **e** padrões locais fortes.

---

# PARTE XIV — CTC

## 27. Connectionist Temporal Classification

Problema: frames acústicos $`T`$ não vêm alinhados token a token com transcript $`Y`$.

CTC introduz paths $`\pi`$ sobre vocabulário + blank.

Collapse operator $`B`$:

- remove repetições consecutivas;
- remove blanks.

Probabilidade:

```math
P(Y|X)
=
\sum_{\pi\in B^{-1}(Y)}P(\pi|X)
```

---

## 28. CTC conditional independence

Forma básica assume frames independentes condicionados ao encoder:

```math
P(\pi|X)=\prod_tP(\pi_t|H_t)
```

Isso facilita decode/alignment, mas limita modeling de dependências entre output tokens.

Language model externo pode ser combinado no beam.

---

## 29. CTC blank

Blank $`\varnothing`$ representa “nenhum novo token”.

Exemplo paths:

```text
-- h h - e - l l - o --
```

collapse:

```text
hello
```

Esse mecanismo resolve diferença entre acoustic frame rate e token rate.

---

# PARTE XV — RNN-T / TRANSDUCER

## 30. Componentes

Encoder acústico:

```math
h_t=Encoder(X)_t
```

Prediction network sobre output anterior:

```math
g_u=Pred(y_{<u})
```

Joint network:

```math
z_{t,u}=Joint(h_t,g_u)
```

```math
P(k|t,u)=softmax(z_{t,u})
```

Isso modela simultaneamente tempo acústico e prefixo textual.

---

## 31. Streaming advantage

Transducer pode operar incrementalmente sem esperar áudio completo.

Latência depende de:

```math
T_{chunk}+T_{lookahead}+T_{encoder}+T_{decode}
```

Não medir apenas RTF total.

---

# PARTE XVI — SEQ2SEQ / SPEECH-LLM ASR

## 32. Encoder–decoder

```math
H=Encoder(audio)
```

```math
P(y_{1:U}|H)=\prod_uP(y_u|y_{<u},H)
```

Whisper-like topology é exemplo clássico.

ASR moderno também pode reutilizar um multimodal/omni backbone e gerar transcript via LM head.

---

## 33. Audio compression before LLM

Se speech encoder produz $`T_a`$ states e LLM context é caro:

```math
T_a\downarrow
```

vira objetivo crítico.

Técnicas:

- strided convolution;
- pooling;
- resampler;
- summary tokens;
- KV compression.

Speech-XL 2026 explora summarization tokens para condensar long-form speech em KV state reduzido.

---

# PARTE XVII — FORCED ALIGNMENT

## 34. O problema

Dado transcript conhecido $`Y`$ e áudio $`X`$:

```math
Align(X,Y)\rightarrow\{(token_i,t_{start},t_{end})\}
```

Não é a mesma tarefa que ASR: conteúdo textual já é conhecido.

---

## 35. Alignment error

Para timestamp verdadeiro $`t_i`$ e estimado $`\hat t_i`$:

```math
e_i=|t_i-\hat t_i|
```

Métricas podem usar mean/median/p95.

Qwen3-ForcedAligner 2026 é exemplo de timestamp predictor não autoregressivo baseado em foundation model.

---

# PARTE XVIII — VAD / ENDPOINTING / DIARIZATION

## 36. Voice Activity Detection

```math
P(speech|frame_t)
```

Threshold + hangover rules definem segmentos.

Endpoint latency:

```math
T_{endpoint}\approx SilenceThreshold+Processing
```

Um ASR perfeito com endpointing ruim parece “lento”.

---

## 37. Speaker diarization

Pergunta:

> quem falou quando?

Output:

```math
\{(speaker_i,t_s,t_e)\}
```

Pipeline pode usar:

- VAD;
- speaker embeddings;
- clustering;
- overlap detection.

Diarization error não é WER.

---

# PARTE XIX — SPEECH UNDERSTANDING

## 38. Speech contém mais que texto

Sinal:

```math
Speech=
Linguistic
+Speaker
+Prosody
+Emotion
+AcousticScene
+NonSpeechEvents
```

ASR extrai principalmente linguistic content.

Speech understanding moderno tenta preservar múltiplas dimensões.

---

## 39. Paralinguistic attributes

Possíveis alvos:

- emotion;
- age/style-like acoustic attributes;
- speaking rate;
- hesitation;
- emphasis;
- turn-taking cues.

O transcript pode ser idêntico enquanto esses estados mudam.

Logo:

```math
Transcript\not\equiv Speech\ Understanding
```

---

## 40. Audio event understanding

Input pode conter:

- siren;
- machinery;
- dog bark;
- music;
- background speech.

Modelos audio-language expandem:

```math
Audio\rightarrow Semantic\ reasoning
```

além de:

```math
Speech\rightarrow Text
```

---

# PARTE XX — STREAMING ECONOMICS

## 41. Real-Time Factor

```math
RTF=\frac{processing\ time}{audio\ duration}
```

```math
RTF<1
```

significa faster-than-real-time para processamento batch/offline.

Mas streaming UX depende também de latency.

---

## 42. Time To First Transcript / partial

```math
TTFT_{speech}
```

é tempo até primeiro resultado útil.

Um sistema pode ter ótimo RTF e péssima first-partial latency.

---

## 43. Chunk size trade-off

Chunk $`C`$:

```math
C\uparrow
\Rightarrow
Context\uparrow,
Latency\uparrow
```

Chunk pequeno reduz latência, mas pode prejudicar phonetic/contextual accuracy e overhead.

---

# PARTE XXI — ASR METRICS

## 44. Word Error Rate

```math
WER=\frac{S+D+I}{N}
```

- S: substitutions;
- D: deletions;
- I: insertions;
- N: words de referência.

WER pode exceder 100%.

---

## 45. Character Error Rate

```math
CER=\frac{S_c+D_c+I_c}{N_c}
```

Útil para idiomas/outputs onde tokenização por palavra é menos estável.

---

## 46. WER não mede tudo

Também medir:

- punctuation;
- casing;
- timestamps;
- named entities;
- numbers;
- language ID;
- diarization;
- streaming latency;
- robustness a noise/music/accent.

Dois ASRs com mesmo WER podem ter UX radicalmente diferente.

---

# PARTE XXII — SNAPSHOT 2026

## Qwen3-ASR

A família 2026 inclui:

- 0.6B / 1.7B;
- language ID + ASR;
- 52 idiomas/dialetos;
- forte eficiência;
- forced aligner não autoregressivo separado.

O ponto arquitetural é a convergência de **speech recognition especializado com representações herdadas de omni foundation models**.

## Speech-XL

Long-form speech está migrando de “aumente contexto” para **comprima estado acústico de forma aprendida**.

## Fine-grained speech understanding

Benchmarks 2026 mostram que bom ASR ainda não implica percepção fina de prosódia, cena acústica e sinais paralinguísticos.

---

# PARTE XXIII — CHECKLIST AUDIO COMPLETO

Ao dissecar qualquer modelo de áudio/speech, identificar:

1. Waveform, spectrogram, codec tokens ou continuous latent?
2. Qual frame/token rate?
3. Tarefa é generation, ASR, VC, understanding ou alignment?
4. Backbone é AR, diffusion, flow, CTC, transducer ou seq2seq?
5. Há speaker/prosody conditioning?
6. É streaming?
7. Qual chunk/lookahead?
8. Qual estado persistente?
9. Qual RTF e first-packet/first-transcript latency?
10. Qual métrica: WER, MOS, FAD, similarity, alignment?
11. O transcript captura tudo que a aplicação precisa?
12. Qual custo por segundo de áudio?

---

## Referências adicionais

- Qwen3-ASR Technical Report — https://arxiv.org/abs/2601.21337
- Speech-XL: Long-Form Speech Understanding — https://arxiv.org/abs/2602.05373
- Fine-Grained Multi-Dimensional Speech Understanding — https://arxiv.org/abs/2605.12036
