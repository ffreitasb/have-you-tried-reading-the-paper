---
title: Evaluation, Benchmarking & Experimentation Datasheet — SOTA++ 2026
aliases: [Evaluation Datasheet, Benchmarking Datasheet, AI Experimentation Reference]
tags: [ai, referencia, avaliacao, benchmarks, experimentacao, estatistica, reproducibilidade]
updated: 2026-10-01
---

# Evaluation, Benchmarking & Experimentation Datasheet — SOTA++ 2026

> Um modelo não “tem performance”. Ele produz uma distribuição de resultados **sob uma configuração experimental específica**. Avaliação é a engenharia necessária para separar ganho real de ruído, harness, prompt, contaminação e wishful thinking.

A equação conceitual central:

\[
\boxed{
ObservedScore
=
f(
Model,
Prompt,
Inference,
Harness,
Dataset,
Metric,
Randomness,
Environment
)
}
\]

Logo:

\[
Score(Model)\quad\text{é geralmente uma abreviação perigosa.}
\]

Veja também:

- [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)
- [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md)

---

# 1. O que exatamente está sendo avaliado?

Antes de calcular qualquer métrica, defina o **System Under Test — SUT**.

Pode ser:

## 1.1 Checkpoint puro

\[
SUT=Weights+Tokenizer
\]

## 1.2 Modelo + prompt/template

\[
SUT=Model+PromptPolicy
\]

## 1.3 Modelo + inferência

\[
SUT=Model+Prompt+Sampler
\]

## 1.4 Pipeline

\[
SUT=Retriever+Reranker+Model
\]

## 1.5 Agente

\[
SUT=Model+Scaffold+Tools+Environment
\]

## 1.6 Produto completo

\[
SUT=EverythingTheUserExperiences
\]

Se o SUT não é explicitado, comparação entre scores pode não ser válida.

---

# 2. Decomposição de erro experimental

Pense:

\[
Y_{ijk}
=
\mu
+M_i
+H_j
+R_k
+\epsilon_{ijk}
\]

onde:

- \(M_i\): efeito do modelo/configuração;
- \(H_j\): efeito do harness/prompt/scaffold;
- \(R_k\): efeito de seed/randomness;
- \(\epsilon\): residual.

Queremos estimar \(M_i\), mas frequentemente medimos todos juntos.

---

# 3. Benchmark ≠ metric ≠ harness

## Benchmark

Define conjunto de tarefas/exemplos/protocolo.

## Metric

Mapeia resultado para escalar/vetor:

\[
Metric(y,\hat y)
\]

## Harness

Executa:

- prompt construction;
- model call;
- decoding;
- parsing;
- scoring;
- aggregation.

Trocar harness pode alterar score mesmo com pesos idênticos.

---

# 4. A unidade experimental mínima

Um registro deveria conter pelo menos:

```yaml
experiment:
  model_id: ...
  model_hash: ...
  tokenizer: ...
  quantization: ...
  backend: ...
  backend_version: ...
  prompt_template: ...
  system_prompt_hash: ...
  context_limit: ...
  generation:
    temperature: ...
    top_p: ...
    min_p: ...
    max_tokens: ...
    seed: ...
  dataset:
    name: ...
    version: ...
    split: ...
    hash: ...
  metric: ...
  hardware: ...
  timestamp: ...
```

Sem versionamento, um resultado vira anedota histórica.

---

# 5. Deterministic metric versus judged metric

## Deterministic

\[
score=g(reference,prediction)
\]

Exemplos:

- exact match;
- test pass/fail;
- numerical tolerance;
- WER;
- retrieval recall.

## Judged

\[
score=Judge(prompt,response,rubric)
\]

É outro modelo/ser humano inferindo qualidade.

Isso adiciona nova fonte de erro:

\[
Var_{judge}
\]

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 6. Accuracy

\[
Accuracy=
\frac{\sum_i\mathbf1(\hat y_i=y_i)}{N}
\]

Simples, mas exige definição inequívoca de “correto”.

Para classes desbalanceadas, accuracy pode ser enganosa.

---

# 7. Precision, Recall e F1

\[
Precision=
\frac{TP}{TP+FP}
\]

\[
Recall=
\frac{TP}{TP+FN}
\]

\[
F1=
2\frac{Precision\cdot Recall}{Precision+Recall}
\]

Macro e micro averaging respondem perguntas diferentes.

---

# 8. Exact Match

\[
EM=
\frac1N\sum_i\mathbf1(normalize(\hat y_i)=normalize(y_i))
\]

A função `normalize()` é parte da métrica.

Mudá-la muda o benchmark.

---

# 9. Pass@k

Em code generation, com \(n\) samples e \(c\) corretos:

\[
pass@k
=
1-
\frac{\binom{n-c}{k}}{\binom nk}
\]

quando condições da estimativa são atendidas.

Pass@1 mede uma realidade diferente de pass@100.

\[
SearchBudget\uparrow
\Rightarrow
pass@k\uparrow
\]

sem que o modelo tenha mudado.

---

# 10. Retrieval metrics

## Recall@K

\[
Recall@K
=
\frac{RelevantRetrieved@K}{TotalRelevant}
\]

## Precision@K

\[
Precision@K
=
\frac{RelevantRetrieved@K}{K}
\]

## MRR

\[
MRR
=
\frac1N
\sum_i
\frac1{rank_i}
\]

## DCG

\[
DCG@K
=
\sum_{i=1}^{K}
\frac{2^{rel_i}-1}{\log_2(i+1)}
\]

## NDCG

\[
NDCG@K
=
\frac{DCG@K}{IDCG@K}
\]

Veja [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 11. Perplexity

Para sequência:

\[
PPL=
\exp\left(
-\frac1T
\sum_t
\log p(x_t|x_{<t})
\right)
\]

É útil para modelagem probabilística, mas:

\[
LowerPPL
\not\Rightarrow
BetterInstructionFollowing
\]

necessariamente.

Comparar PPL entre tokenizers diferentes exige extremo cuidado.

---

# 12. Calibration

Se modelo diz probabilidade \(p\), queremos:

\[
P(correct|confidence=p)\approx p
\]

## Brier score

\[
BS=
\frac1N\sum_i(p_i-y_i)^2
\]

## ECE

Agrupa previsões por bins e mede diferença entre confidence e accuracy.

Calibration é distinta de accuracy.

---

# 13. ASR

## Word Error Rate

\[
WER=
\frac{S+D+I}{N}
\]

onde:

- \(S\): substitutions;
- \(D\): deletions;
- \(I\): insertions.

Veja [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

---

# 14. Time-series metrics

## MAE

\[
MAE=
\frac1N\sum_i|y_i-\hat y_i|
\]

## RMSE

\[
RMSE=
\sqrt{
\frac1N\sum_i(y_i-\hat y_i)^2
}
\]

## MAPE caveat

\[
MAPE=
\frac{100}{N}
\sum_i
\left|
\frac{y_i-\hat y_i}{y_i}
\right|
\]

explode ou fica instável quando \(y_i\approx0\).

Probabilistic forecasts exigem métricas próprias de distribuição/quantis.

Veja [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).

---

# 15. Image/video/audio generation

Não existe uma única “quality metric” suficiente.

Dimensões distintas:

- fidelity;
- prompt adherence;
- identity consistency;
- temporal consistency;
- perceptual quality;
- diversity;
- human preference.

Logo:

\[
Quality
\in
\mathbb R^d
\]

não necessariamente:

\[
Quality\in\mathbb R
\]

Um único scalar ranking esconde trade-offs.

---

# 16. 3D evaluation

Pode incluir:

- Chamfer distance;
- normal consistency;
- IoU;
- watertightness;
- non-manifold edges;
- geometric validity;
- render-space perceptual metrics.

Para fabricação:

\[
Printable\neq VisuallyPlausible
\]

Veja [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md).

---

# 17. Agent evaluation

Agentes precisam métricas além do texto final:

\[
SuccessRate
\]

\[
StepsToSuccess
\]

\[
ToolCalls
\]

\[
Cost
\]

\[
UnsafeActions
\]

\[
RecoveryRate
\]

\[
StateValidity
\]

Uma resposta bonita pode acompanhar uma trajetória operacional péssima.

---

# 18. World/VLA evaluation

Precisamos separar:

- prediction accuracy;
- rollout fidelity;
- action success;
- collision/safety rate;
- horizon degradation;
- sim-to-real gap.

World-model error pode acumular:

\[
\epsilon_{t+H}
=f(\epsilon_t,H,dynamics)
\]

Veja [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md).

---

# 19. Statistical uncertainty não é opcional

Um score observado é amostra:

\[
\hat\mu
\]

Queremos estimar:

\[
\mu
\]

com incerteza.

---

# 20. Standard error

Para média:

\[
SE=
\frac{s}{\sqrt N}
\]

Crescer \(N\) reduz incerteza aproximadamente como:

\[
1/\sqrt N
\]

Não linearmente com N.

---

# 21. Confidence interval

Forma assintótica simples:

\[
CI
\approx
\hat\mu
\pm
z_{\alpha/2}SE
\]

Para muitos benchmarks, bootstrap é mais flexível.

---

# 22. Bootstrap

1. amostrar exemplos com reposição;
2. recalcular métrica;
3. repetir \(B\) vezes;
4. obter distribuição empírica.

\[
\{\hat\theta_1^*,\ldots,\hat\theta_B^*\}
\]

Útil para métricas sem fórmula simples de variância.

---

# 23. Paired design

Se modelos A e B respondem aos **mesmos itens**, use diferença pareada:

\[
d_i=s_i(A)-s_i(B)
\]

Então estude:

\[
\bar d
\]

Isso remove parte da variação devido à dificuldade entre itens.

É geralmente melhor que comparar médias como amostras independentes.

---

# 24. McNemar para acerto/erro pareado

Para classificação binária, conte discordâncias:

- A certo / B errado: \(b\)
- A errado / B certo: \(c\)

A evidência de diferença vem de \(b\) versus \(c\), não de acertos totais isolados.

---

# 25. Permutation test

Sob hipótese nula de troca de labels/configurações, permute pares e calcule distribuição de \(\Delta\).

É útil quando não queremos assumir normalidade.

---

# 26. Effect size

Significância estatística não implica relevância prática.

Pergunte:

\[
|\Delta|\quad\text{é grande o suficiente para justificar custo/risco?}
\]

Exemplo:

+0,2 ponto de benchmark pode não compensar +70% de VRAM.

---

# 27. Multiple comparisons

Se testar centenas de configurações, algum “ganhador” aparece por acaso.

\[
P(false\ positive)\uparrow
\]

com número de hipóteses.

Use:

- held-out final set;
- correction quando apropriado;
- preregistered hypotheses;
- evitar escolher seed/configuração pelo test set.

---

# 28. Seed variance

Para stochastic generation:

\[
Y_{m,s}
\]

onde \(s\) é seed.

Calcule:

\[
Var_s(Y|m)
\]

antes de interpretar diferença entre modelos.

Se:

\[
|\Delta_{models}|
<
\sigma_{seed}
\]

um único run é evidência fraca.

---

# 29. Hierarchical variance

Em benchmark com tasks, examples e seeds:

\[
Y_{task,item,seed}
\]

podemos decompor variância em múltiplos níveis.

Isso mostra se resultado é dominado por:

- algumas categorias;
- alguns itens;
- randomness.

Macro-average pode esconder tudo isso.

---

# 30. Stochastic benchmark protocol

Para geração livre:

```text
for model/config:
    for item:
        for seed in S:
            generate
            score
```

Depois reportar:

- mean;
- median;
- std/IQR;
- CI;
- failure rate;
- tails.

---

# 31. Tail metrics

Usuário não experimenta “a média” apenas.

Em latency:

\[
p50,p95,p99
\]

Em safety/reliability:

worst-case e failure-tail podem dominar risco.

Para agents:

\[
P(catastrophic\ failure)
\]

pode ser mais importante que mean success rate.

---

# 32. Benchmark contamination

Tipos:

## Exact contamination

Item idêntico no treino.

## Near-duplicate

Paráfrase/transformação.

## Solution contamination

Resposta/solução aparece em dados.

## Benchmark-aware post-training

Modelo foi explicitamente otimizado para benchmark.

Mesmo sem leakage literal, score deixa de ser estimativa neutra de generalização.

---

# 33. Benchmark saturation

Se quase todos os modelos relevantes estão perto do teto:

\[
Var_{models}(score)\rightarrow0
\]

benchmark perde poder discriminativo.

Pesquisa de 2026 analisando 60 benchmarks encontrou saturação em uma parcela grande e crescente com idade; expert-curated benchmarks mostraram maior resistência que crowdsourced em média.

A lição:

\[
BenchmarkHalfLife<\infty
\]

---

# 34. Dynamic benchmarks

Benchmarks atualizados periodicamente tentam reduzir contamination e saturation.

LiveBench exemplifica:

- perguntas renovadas;
- fontes recentes;
- ground truth objetivo quando possível;
- múltiplas categorias.

Mas atualização também significa:

\[
Score_{2025}\not\equiv Score_{2026}
\]

sem versionamento do dataset.

---

# 35. Public versus private test

Private test data reduz exposição direta, mas não elimina:

- conceptual leakage;
- benchmark-targeted optimization;
- saturation;
- similar training examples.

Portanto:

\[
Private\neq ContaminationProof
\]

---

# 36. LLM-as-a-Judge

Judge:

\[
J(prompt,response,rubric)
\rightarrow score/verdict
\]

Problemas comuns:

- position bias;
- verbosity bias;
- style bias;
- self-preference;
- reference anchoring;
- domain mismatch.

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 37. Swap test

Para pairwise judge:

1. julgar A,B;
2. trocar ordem B,A;
3. comparar.

Se:

\[
J(A,B)\neq reverse(J(B,A))
\]

há inconsistência/position sensitivity.

---

# 38. Rubric decomposition

Em vez de score monolítico:

\[
Quality
=
(w_1q_1,\ldots,w_kq_k)
\]

Dimensões possíveis:

- correctness;
- completeness;
- relevance;
- style;
- safety;
- evidence.

Isso melhora auditabilidade.

---

# 39. Human evaluation

Human eval não é ground truth mágico.

Tem:

- inter-rater disagreement;
- fatigue;
- rubric ambiguity;
- expertise variation;
- context effects.

Métricas de agreement ajudam a quantificar consistência.

---

# 40. Model versus scaffold

Coding-agent benchmark mede frequentemente:

\[
Model
+
AgentLoop
+
Tools
+
Prompt
+
Search
+
RetryBudget
\]

não apenas o model checkpoint.

SWE-bench Verified, por exemplo, explicitamente compara sistemas que vão de simple loops a RAG/multi-rollout/review systems.

Portanto leaderboard de agents não é leaderboard puro de LLMs.

---

# 41. Harness sensitivity

Mudanças pequenas em:

- few-shot examples;
- answer parsing;
- stop sequence;
- whitespace;
- chat template;
- reasoning budget;

podem mudar resultados.

Um benchmark sem harness versionado não é plenamente reproduzível.

---

# 42. Quality versus test-time compute

Se configuração A usa:

\[
N_A=1
\]

sample e B usa:

\[
N_B=64
\]

+ verifier,

não estamos comparando apenas modelos.

Estamos comparando:

\[
Model\times SearchBudget
\]

Reportar:

\[
Quality(Cost)
\]

é mais honesto.

---

# 43. Best-of-N evaluation

Gere:

\[
y_1,\ldots,y_N
\]

Selecione:

\[
y^*=\arg\max_i V(y_i)
\]

Score cresce com:

- generator diversity;
- N;
- verifier quality.

Atribuir todo ganho ao generator é erro causal.

---

# 44. Runtime evaluation

## TTFT

Time To First Token.

Se request inicia em \(t_0\) e primeiro token chega em \(t_1\):

\[
TTFT=t_1-t_0
\]

## Inter-token latency / TPOT

Tempo médio por token depois do primeiro.

## Generation TPS

\[
TPS=
\frac{N_{generated}}{T_{decode}}
\]

## Throughput

\[
Throughput=
\frac{TotalTokens}{WallClock}
\]

TPS single-user e throughput server são objetivos diferentes.

---

# 45. Prefill versus decode benchmark

Nunca misturar:

\[
PromptTPS
\]

com:

\[
DecodeTPS
\]

Veja [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

Prefill é muito mais paralelizável; decode frequentemente é memory-bandwidth bound.

---

# 46. Memory metric

Registrar:

- model load VRAM;
- idle VRAM;
- peak prefill;
- peak decode;
- host RAM;
- KV allocation;
- temporary workspace.

Um número “VRAM usada” sem fase de execução é ambíguo.

---

# 47. Energy / efficiency

Quando disponível:

\[
EnergyPerToken
=
\frac{\int P(t)dt}{N_{tokens}}
\]

Ou:

\[
J/request
\]

Para local inference, performance/W pode alterar decisão de hardware tanto quanto TPS.

---

# 48. Pareto analysis

Em vez de procurar “melhor modelo”, construa vetor:

\[
z=
(Quality,Latency,Memory,Cost,Context)
\]

Modelo é Pareto-dominado se existe outro melhor ou igual em todas as dimensões e estritamente melhor em pelo menos uma.

Para uma RTX 2060 12 GB:

\[
VRAM\le12GB
\]

é constraint real, não coluna decorativa.

---

# 49. Quality per physical budget

Métricas úteis:

\[
Quality/GB
\]

\[
Quality/Joule
\]

\[
Quality/Second
\]

\[
Quality/TokenBudget
\]

especialmente para comparar quantizações e model sizes.

---

# 50. Quantization experiment

Ao comparar Q4 vs Q5:

**Controlar:**

- model source;
- context;
- sampler;
- backend;
- prompt set.

**Observar:**

- task quality;
- logit divergence se possível;
- VRAM;
- TPS;
- TTFT.

A pergunta é:

\[
\frac{\Delta Quality}{\Delta Memory}
\]

e:

\[
\frac{\Delta Quality}{\Delta Throughput}
\]

---

# 51. A/B sampler experiment

Para comparar Min-P:

- mesmo model;
- mesmo prompt set;
- mesmo seed set quando backend permite;
- demais samplers fixos;
- múltiplas outputs.

Não use “achei este texto mais bonito” como única estatística.

Capture:

- repetition rate;
- lexical diversity;
- judge rubric;
- human pairwise preference;
- failure counts.

---

# 52. Evaluation dataset design

Amostra deve cobrir distribuição alvo:

\[
D_{eval}\sim D_{deployment}
\]

na medida do possível.

Se benchmark é academia e deployment é atendimento B2B em português:

\[
ExternalValidity\downarrow
\]

mesmo com score excelente.

---

# 53. Slice analysis

Nunca só aggregate score.

Particione por:

- idioma;
- dificuldade;
- comprimento;
- domínio;
- modality;
- risk level;
- tool type.

Pode ocorrer:

\[
Mean_A>Mean_B
\]

mas:

\[
A<B
\]

no slice crítico para produção.

---

# 54. Regression suite

Após escolher sistema, mantenha conjunto fixo de regressões:

```text
must-pass
known-hard
known-failure
security
format
latency
```

Cada atualização roda novamente.

Isso transforma benchmark em **controle de processo**.

---

# 55. Golden cases

Casos pequenos, semanticamente importantes, inspecionados manualmente.

Não substituem benchmark amplo.

Servem para detectar regressões óbvias com alta interpretabilidade.

---

# 56. Canary tests

Casos desenhados para detectar uma falha específica.

Exemplo:

- template corruption;
- context truncation;
- tool hallucination;
- unicode/tokenizer bug.

Canary bom tem causalidade clara.

---

# 57. Adversarial evaluation

Avaliação normal mede distribuição nominal.

Adversarial eval mede vizinhança hostil:

\[
x' = x+\delta
\]

ou inputs deliberadamente construídos para falhar.

Veja [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

# 58. Evaluation leakage via development loop

Mesmo sem treinar pesos:

se você olha o test set repetidamente e ajusta prompt/configuração:

\[
TestSet\rightarrow DevelopmentSignal
\]

Então deixou de ser test set puro.

Mantenha:

- dev set;
- final holdout.

---

# 59. Benchmark overfitting organizacional

Equipe pode otimizar KPI até perder validade externa.

\[
Leaderboard\uparrow
\not\Rightarrow
RealWorldUtility\uparrow
\]

Esse é Goodhart aplicado à avaliação.

---

# 60. Benchmark retirement

Critérios para aposentar ou rebaixar benchmark:

- saturation;
- contamination conhecida;
- poor external validity;
- metric no longer relevant;
- harness ambiguity;
- task obsolete.

Não há mérito em preservar comparabilidade histórica às custas de sinal atual.

---

# 61. Snapshot SOTA 2026

Pontos particularmente relevantes em outubro de 2026:

1. Benchmark contamination deixou de ser caveat periférico; é variável de design central.
2. Estudos de 2026 mostram saturação ampla em benchmarks antigos e reforçam necessidade de suites rotativas e expert-curated.
3. Live/dynamic benchmarks são uma resposta útil, mas exigem versionamento temporal.
4. LLM-as-a-Judge escalou avaliação aberta, porém position/verbosity/style/calibration bias precisam ser medidos, não presumidos ausentes.
5. Coding-agent evaluation tornou explícita a distinção **model vs scaffold/system**.
6. HELM permanece referência conceitual de holistic/reproducible evaluation, embora o projeto geral tenha entrado em maintenance mode em junho de 2026; isso reforça a necessidade de evitar dependência de um único harness.
7. Avaliação moderna é multiobjetivo: capability, reliability, safety, latency, memory e cost devem aparecer juntos.

---

# 62. Experiment card — template recomendado

```markdown
## Hypothesis

## System under test

## Independent variable

## Controlled variables

## Dataset + version + hash

## Metric definitions

## Seed/repetition policy

## Hardware/runtime

## Results
- mean:
- median:
- std/IQR:
- confidence interval:
- failure count:

## Paired differences

## Slice analysis

## Physical cost
- VRAM:
- RAM:
- TTFT:
- TPS:
- energy/cost:

## Decision rule

## Caveats
```

---

# 63. Decision rule antes do experimento

Defina antes:

\[
Accept\ A
\quad\text{if}\quad
\Delta Q>\delta_{min}
\]

sujeito a:

\[
Memory<M_{max}
\]

\[
Latency<L_{max}
\]

Isso reduz post-hoc rationalization.

---

# 64. Minimal local-model test battery

Para seu stack local, eu manteria pelo menos:

1. task accuracy / instruction adherence;
2. Portuguese naturalness;
3. code correctness se aplicável;
4. long-context retrieval;
5. repetition/degeneration;
6. structured-output validity;
7. TTFT;
8. decode TPS;
9. peak VRAM/RAM;
10. context scaling;
11. failure cases próprios;
12. safety/tool tests se agentic.

Essa bateria deve ser mais valiosa para decisão local que uma posição isolada em leaderboard público.

---

# 65. A equação final

\[
\boxed{
Evidence
=
Measurement
+
Uncertainty
+
Protocol
+
Reproducibility
}
\]

Sem uncertainty, temos número.

Sem protocol, temos benchmark folklore.

Sem reproducibility, temos anedota.

---

# Checklist de qualquer benchmark que aparecer amanhã

1. Qual SUT está sendo medido?
2. Modelo puro ou sistema?
3. Qual dataset version?
4. Público ou privado?
5. Há contamination evidence?
6. Está saturado?
7. Qual métrica?
8. A métrica é objetiva ou judged?
9. Qual judge?
10. Judge foi calibrado?
11. Houve order-swap?
12. Quantos samples/seed?
13. Qual inference budget?
14. Qual prompt/template?
15. Qual harness/version?
16. Qual context limit?
17. Quantização?
18. Hardware/backend?
19. Há CI/variance?
20. Comparação é pareada?
21. Há slice analysis?
22. Há custo físico?
23. Qual external validity?
24. Score melhora algo que importa?
25. Decisão muda se benchmark variar dentro do CI?

---

# Referências snapshot

- LiveBench — https://arxiv.org/abs/2406.19314
- LiveBench ICLR 2025 — https://proceedings.iclr.cc/paper_files/paper/2025/hash/e4a46394ba5378b3f9a186a5b4c650d1-Abstract-Conference.html
- When AI Benchmarks Plateau — https://proceedings.mlr.press/v306/akhtar26a.html
- HELM — https://github.com/stanford-crfm/helm
- SWE-bench Verified — https://www.swebench.com/verified.html
- Judging the Judges: Position Bias — https://arxiv.org/abs/2406.07791
- Mitigating the Bias of Large Language Model Evaluation — https://arxiv.org/abs/2409.16788
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) for 2026 judge/reward references
