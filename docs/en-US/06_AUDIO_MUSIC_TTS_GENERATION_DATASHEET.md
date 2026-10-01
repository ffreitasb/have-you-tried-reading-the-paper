---
title: Audio, Speech, Music & TTS Model Datasheet v3.0
tags: [ai, audio, speech, music, tts, asr, codec, diffusion, streaming]
updated: 2026-10-01
---

# Audio, Speech, Music & TTS Model Datasheet v3.0

> Generative audio is not a single family. The decisive variable is **how the waveform was compressed/represented before generation**.

## 1. Three major pipelines

### A. Codec-token autoregression

\[
waveform\rightarrow codec\ tokens\rightarrow LM\rightarrow codec\ decoder\rightarrow waveform
\]

### B. Latent diffusion/flow

\[
waveform\rightarrow AE\ latent\rightarrow diffusion/flow\rightarrow decoder\rightarrow waveform
\]

### C. TTS/voice systems

\[
text+speaker/style\rightarrow linguistic/acoustic\ representation\rightarrow acoustic\ decoder/vocoder
\]

Voice conversion adds another class:

\[
source\ speech\rightarrow content/prosody\rightarrow target\ timbre
\]

Do not conflate TTS with VC.

---

# PART I — REPRESENTATION

## 2. Waveform

\[
x\in\mathbb{R}^{channels\times samples}
\]

For sample rate \(f_s\) and duration \(D\):

\[
N_{samples}=f_sD
\]

44.1 kHz stereo for 60 s:

\[
44,100\cdot60\cdot2\approx5.29\text{ million samples}
\]

Generating directly at that length is expensive; that is why codecs/autoencoders compress time.

---

## 3. Codec tokens

Codec frame rate:

\[
r_c=\frac{frames}{second}
\]

With \(K\) codebooks:

\[
tokens/sec\approx r_cK
\]

Duration:

\[
T_{tokens}\approx D\,r_cK
\]

This directly links duration to sequence length.

---

## 4. Semantic vs acoustic tokens

A codec may prioritize:

- semantic content;
- timbre/prosody;
- detailed acoustic reconstruction;
- low bitrate/streaming.

Multiple codebooks may decompose information into discrete layers.

Qwen3-TTS in 2026 illustrates two regimes: a 25 Hz single-codebook tokenizer focused on semantics and a 12.5 Hz multi-codebook tokenizer targeting extremely low bitrate/latency.

---

## 5. Continuous audio latents

Autoencoder:

\[
Z=E(x),\qquad \hat x=D(Z)
\]

Latent rate:

\[
r_l=\frac{N_{latent\ frames}}{D}
\]

Stable Audio 3 uses a semantic-acoustic autoencoder to reduce sequence length dramatically before generation.

---

# PART II — MUSIC/AUDIO AUTOREGRESSIVE

## 6. Next audio token

\[
p(a_{1:T})=\prod_tp(a_t\mid a_{<t},C)
\]

The usual controls apply:

- temperature;
- top-k/top-p;
- repetition behavior;
- KV/context limits.

### Caveat

Top-K does not “cut frequencies.” It filters **discrete codec/vocabulary tokens**.

---

## 7. Duration

For an autoregressive codec:

\[
Compute\propto T_{tokens}
\]

KV/cache also grows with sequence length if the architecture is a conventional causal Transformer.

---

# PART III — LATENT DIFFUSION/FLOW

## 8. Diffusion

\[
z_t=\alpha_tz_0+\sigma_t\epsilon
\]

The network predicts noise/velocity/clean latent.

### Flow

\[
\frac{dz_t}{dt}=v_\theta(z_t,t,C)
\]

The same concepts apply:

- steps;
- schedule;
- solver;
- CFG;
- seed.

But the relevant axis is now time/feature channels rather than image space.

---

## 9. Variable-length generation

Modern models may avoid always generating one fixed maximum window.

Cost depends on latent length:

\[
N_l\propto duration
\]

If attention is global:

\[
C_{attn}\sim O(N_l^2)
\]

So “VRAM grows linearly with duration” is only partly true: **state** may grow linearly while attention compute/activations may grow superlinearly.

---

# PART IV — TTS

## 10. TTS decomposed

\[
Text\rightarrow semantic/linguistic\ units\rightarrow acoustic\ representation\rightarrow waveform
\]

Additional conditioning:

\[
C=\{speaker,style,language,prosody,reference\}
\]

---

## 11. Speaker similarity

There is no universal mathematical knob called “Similarity Boost.” That is a product-level abstraction in some systems.

The underlying mechanism may involve:

- speaker embedding;
- reference encoder;
- prompt audio tokens;
- latent conditioning.

Voice adherence depends on distance/compatibility in speaker-representation space, the training distribution, and reference quality.

---

## 12. Stability

This is not a universal mathematical variable either. It may map to:

- sampling entropy;
- style/prosody variance;
- deterministic paths;
- vendor-specific interpolation.

Classify `Stability` as `UI` until you know its implementation.

---

## 13. Prosody

Prosody includes:

- F0/pitch;
- duration/rhythm;
- energy;
- pauses;
- emphasis.

Voice-timbre cloning and prosody transfer are different problems.

---

# PART V — SPEECH-TO-SPEECH / VOICE CONVERSION

## 14. VC

Idealized objective:

\[
y=D(content(x),prosody(x),speaker_{target})
\]

RVC-like systems belong here.

XTTS-like systems are primarily TTS/voice-cloning systems, even when used in workflows that preserve some style through reference audio.

---

# PART VI — STREAMING

## 15. First-packet latency

For interactive TTS:

\[
Latency_{perceived}\approx T_{first\ audio\ packet}
\]

This is not the same as total synthesis time.

Causal/blockwise architectures can begin playback before generation is complete.

Qwen3-TTS reports a dual-track architecture and streaming-capable decoders, illustrating this distinction.

---

# PART VII — CONDITIONING

## 16. Text prompt

Music/SFX:

\[
C_{text}=Encoder(description)
\]

### Audio prompt/reference

\[
C_{audio}=E_{ref}(waveform)
\]

It may control:

- melody;
- rhythm;
- timbre;
- continuation;
- structure.

The mechanism is model-dependent; “whistle a melody and swap the instrument” is not a universal capability.

---

# PART VIII — EDITING

## 17. Audio inpainting

Temporal mask \(M\):

\[
z'=M\odot z_{generated}+(1-M)\odot z_{reference}
\]

This allows replacing an interval while preserving context before and after it.

### Continuation

Conditioning on the prefix:

\[
p(audio_{future}\mid audio_{past},C)
\]

or a partially conditioned flow/diffusion process.

---

# PART IX — GUIDANCE AND SAMPLING

## 18. Autoregressive

Use token sampling.

## 19. Diffusion/flow

Use solver/schedule/guidance.

### Golden rule

Do not mix controls from different model families merely because they appear in the same UI.

`Top-K` only makes sense when a discrete distribution is being sampled at that stage.

`Steps` only makes sense when there is an iterative trajectory at that stage.

---

# PART X — QUALITY OBSERVABLES

## 20. Metrics

### Speech

- WER/CER;
- speaker-similarity embedding;
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

No single metric replaces listening tests across all objectives.

---

# PART XI — COUPLING MATRIX

| Control ↑ | Diversity | Prompt adherence | Compute | Voice identity |
|---|---:|---:|---:|---:|
| AR temperature | ↑ | may ↓ | ~ | may ↓ |
| diffusion steps | ~ | may ↑ until plateau | ↑ | — |
| CFG | ↓ | ↑ until useful regime | ↑ | depends |
| duration | — | — | ↑ | drift risk ↑ |
| reference strength | ↓ | — | varies | ↑ |
| codec bitrate | reconstruction ↑ | — | token/decoder cost ↑ | potential ↑ |

---

# PART XII — FAILURE DIAGNOSTICS

| Symptom | Investigate |
|---|---|
| voice changes across long text | speaker conditioning/context/streaming state |
| wrong words | linguistic model/tokenizer |
| metallic/phasey sound | codec/vocoder/flow guidance |
| music enters a loop | AR sampling/context/model prior |
| editing artifact | mask boundaries/latent codec |
| excessive VRAM on long duration | latent/token length/attention |

---

## 21. Snapshot 2026

- Qwen3-TTS: dual-track LM, 25 Hz and 12.5 Hz codecs, streaming, and blockwise DiT/causal decoding depending on the variant.
- Stable Audio 3: semantic-acoustic autoencoder + latent diffusion; variable-length generation, inpainting, and adversarial post-training for fewer inference steps.

## References

- Qwen3-TTS — https://arxiv.org/abs/2601.15621
- Stable Audio 3 — https://arxiv.org/abs/2605.17991

---

# PART XIII — AUTOMATIC SPEECH RECOGNITION (ASR)

> TTS does not simply run backward to become ASR. The inverse problem has latent alignment, acoustic noise, multiple speakers, endpointing, and a different objective function.

Related: [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

## 22. Classical/modern acoustic pipeline

\[
waveform
\rightarrow frontend/encoder
\rightarrow H_{speech}
\rightarrow recognition\ head/decoder
\rightarrow text
\]

The frontend may use:

- log-Mel spectrogram;
- learned convolutional frontend;
- speech tokenizer/codec;
- pretrained speech encoder.

---

## 23. STFT

For window \(w[n]\):

\[
X(m,k)=\sum_n x[n]w[n-mR]e^{-j2\pi kn/N}
\]

where \(R\) is the hop size.

The STFT creates a time-frequency representation.

---

## 24. Mel filterbank

Frequency in Hz is mapped approximately to the perceptual Mel scale:

\[
m=2595\log_{10}\left(1+\frac{f}{700}\right)
\]

Log-Mel:

\[
F=\log(Mel(|STFT(x)|^2)+\epsilon)
\]

Many modern ASR systems still begin with something equivalent to this, even when the backbone is a Transformer or Conformer.

---

## 25. Acoustic frame rate

If the hop is \(R\) samples and sample rate is \(f_s\):

\[
r_f=\frac{f_s}{R}
\]

frames/s.

For audio of duration \(D\):

\[
T_f\approx D\,r_f
\]

Long-form speech can therefore explode sequence length before any LLM is involved.

---

## 26. Conformer

Combines global/contextual attention with local convolution:

\[
H'
=H+\frac12FFN(H)
\]

\[
H''=H'+MHSA(H')
\]

\[
H'''=H''+Conv(H'')
\]

\[
Y=LayerNorm(H'''+\frac12FFN(H'''))
\]

The idea: speech contains both global dependencies **and** strong local patterns.

---

# PART XIV — CTC

## 27. Connectionist Temporal Classification

Problem: acoustic frames \(T\) are not aligned token-for-token with transcript \(Y\).

CTC introduces paths \(\pi\) over the vocabulary + blank symbol.

Collapse operator \(B\):

- removes consecutive repetitions;
- removes blanks.

Probability:

\[
P(Y|X)
=
\sum_{\pi\in B^{-1}(Y)}P(\pi|X)
\]

---

## 28. CTC conditional independence

The basic form assumes frames are independent conditioned on the encoder:

\[
P(\pi|X)=\prod_tP(\pi_t|H_t)
\]

This simplifies decoding/alignment, but limits modeling of dependencies among output tokens.

An external language model can be combined during beam search.

---

## 29. CTC blank

Blank \(\varnothing\) represents “no new token.”

Example path:

```text
-- h h - e - l l - o --
```

collapse:

```text
hello
```

This mechanism resolves the mismatch between acoustic frame rate and token rate.

---

# PART XV — RNN-T / TRANSDUCER

## 30. Components

Acoustic encoder:

\[
h_t=Encoder(X)_t
\]

Prediction network over previous output:

\[
g_u=Pred(y_{<u})
\]

Joint network:

\[
z_{t,u}=Joint(h_t,g_u)
\]

\[
P(k|t,u)=softmax(z_{t,u})
\]

This jointly models acoustic time and the textual prefix.

---

## 31. Streaming advantage

A transducer can operate incrementally without waiting for the complete audio.

Latency depends on:

\[
T_{chunk}+T_{lookahead}+T_{encoder}+T_{decode}
\]

Do not measure only total RTF.

---

# PART XVI — SEQ2SEQ / SPEECH-LLM ASR

## 32. Encoder–decoder

\[
H=Encoder(audio)
\]

\[
P(y_{1:U}|H)=\prod_uP(y_u|y_{<u},H)
\]

Whisper-like topology is the classic example.

Modern ASR may also reuse a multimodal/omni backbone and generate the transcript through an LM head.

---

## 33. Audio compression before the LLM

If the speech encoder produces \(T_a\) states and LLM context is expensive:

\[
T_a\downarrow
\]

becomes a critical objective.

Techniques:

- strided convolution;
- pooling;
- resampler;
- summary tokens;
- KV compression.

Speech-XL 2026 explores summarization tokens to condense long-form speech into a reduced KV state.

---

# PART XVII — FORCED ALIGNMENT

## 34. The problem

Given known transcript \(Y\) and audio \(X\):

\[
Align(X,Y)\rightarrow\{(token_i,t_{start},t_{end})\}
\]

This is not the same task as ASR: the textual content is already known.

---

## 35. Alignment error

For true timestamp \(t_i\) and estimate \(\hat t_i\):

\[
e_i=|t_i-\hat t_i|
\]

Metrics may use mean/median/p95.

Qwen3-ForcedAligner 2026 is an example of a non-autoregressive timestamp predictor built on a foundation model.

---

# PART XVIII — VAD / ENDPOINTING / DIARIZATION

## 36. Voice Activity Detection

\[
P(speech|frame_t)
\]

Threshold + hangover rules define segments.

Endpoint latency:

\[
T_{endpoint}\approx SilenceThreshold+Processing
\]

Perfect ASR with poor endpointing still feels “slow.”

---

## 37. Speaker diarization

Question:

> who spoke when?

Output:

\[
\{(speaker_i,t_s,t_e)\}
\]

A pipeline may use:

- VAD;
- speaker embeddings;
- clustering;
- overlap detection.

Diarization error is not WER.

---

# PART XIX — SPEECH UNDERSTANDING

## 38. Speech contains more than text

Signal:

\[
Speech=
Linguistic
+Speaker
+Prosody
+Emotion
+AcousticScene
+NonSpeechEvents
\]

ASR extracts primarily linguistic content.

Modern speech understanding attempts to preserve multiple dimensions.

---

## 39. Paralinguistic attributes

Possible targets:

- emotion;
- age/style-like acoustic attributes;
- speaking rate;
- hesitation;
- emphasis;
- turn-taking cues.

The transcript may be identical while these states change.

Therefore:

\[
Transcript\not\equiv Speech\ Understanding
\]

---

## 40. Audio event understanding

Input may contain:

- siren;
- machinery;
- dog bark;
- music;
- background speech.

Audio-language models extend:

\[
Audio\rightarrow Semantic\ reasoning
\]

beyond:

\[
Speech\rightarrow Text
\]

---

# PART XX — STREAMING ECONOMICS

## 41. Real-Time Factor

\[
RTF=\frac{processing\ time}{audio\ duration}
\]

\[
RTF<1
\]

means faster-than-real-time processing for batch/offline workloads.

But streaming UX also depends on latency.

---

## 42. Time To First Transcript / partial

\[
TTFT_{speech}
\]

is the time until the first useful result.

A system may have excellent RTF and terrible first-partial latency.

---

## 43. Chunk-size trade-off

Chunk \(C\):

\[
C\uparrow
\Rightarrow
Context\uparrow,
Latency\uparrow
\]

Small chunks reduce latency, but may hurt phonetic/contextual accuracy and increase overhead.

---

# PART XXI — ASR METRICS

## 44. Word Error Rate

\[
WER=\frac{S+D+I}{N}
\]

- S: substitutions;
- D: deletions;
- I: insertions;
- N: reference words.

WER can exceed 100%.

---

## 45. Character Error Rate

\[
CER=\frac{S_c+D_c+I_c}{N_c}
\]

Useful for languages/outputs where word-level tokenization is less stable.

---

## 46. WER does not measure everything

Also measure:

- punctuation;
- casing;
- timestamps;
- named entities;
- numbers;
- language ID;
- diarization;
- streaming latency;
- robustness to noise/music/accent.

Two ASR systems with the same WER can have radically different UX.

---

# PART XXII — SNAPSHOT 2026

## Qwen3-ASR

The 2026 family includes:

- 0.6B / 1.7B;
- language ID + ASR;
- 52 languages/dialects;
- strong efficiency;
- separate non-autoregressive forced aligner.

The architectural point is the convergence of **specialized speech recognition with representations inherited from omni foundation models**.

## Speech-XL

Long-form speech is moving from “increase context” to **learned compression of acoustic state**.

## Fine-grained speech understanding

2026 benchmarks show that strong ASR still does not imply fine-grained perception of prosody, acoustic scenes, and paralinguistic signals.

---

# PART XXIII — COMPLETE AUDIO CHECKLIST

When dissecting any audio/speech model, identify:

1. Waveform, spectrogram, codec tokens, or continuous latent?
2. What frame/token rate?
3. Is the task generation, ASR, VC, understanding, or alignment?
4. Is the backbone AR, diffusion, flow, CTC, transducer, or seq2seq?
5. Is there speaker/prosody conditioning?
6. Is it streaming?
7. What chunk/lookahead?
8. What persistent state?
9. What RTF and first-packet/first-transcript latency?
10. Which metric: WER, MOS, FAD, similarity, alignment?
11. Does the transcript capture everything the application needs?
12. What is the cost per second of audio?

---

## Additional references

- Qwen3-ASR Technical Report — https://arxiv.org/abs/2601.21337
- Speech-XL: Long-Form Speech Understanding — https://arxiv.org/abs/2602.05373
- Fine-Grained Multi-Dimensional Speech Understanding — https://arxiv.org/abs/2605.12036
