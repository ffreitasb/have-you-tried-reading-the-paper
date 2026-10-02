---
title: Time-Series & Tabular Foundation Models Datasheet v1.0
tags: [ai, time-series, tabular, forecasting, tabpfn, foundation-models]
updated: 2026-10-01
---

# Time-Series & Tabular Foundation Models Datasheet v1.0

> Números estruturados não são “texto com vírgulas”. Séries temporais têm ordem física e dependência temporal; tabelas têm features heterogêneas, missingness e simetrias diferentes. Foundation models nesses domínios precisam de uma física própria de representação.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md), [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# PARTE A — TIME SERIES FOUNDATION MODELS

# 1. Estado fundamental

Série multivariada:

```math
X=(x_1,\ldots,x_T),\quad x_t\in\mathbb R^D
```

Diferente de texto:

- posição corresponde a tempo físico;
- valores possuem escala/unidade;
- sampling interval importa;
- trend/seasonality/regime são propriedades do processo gerador.

---

# 2. Forecasting

Histórico:

```math
X_{1:T}
```

Horizonte:

```math
H
```

Predição pontual:

```math
\hat X_{T+1:T+H}=f_\theta(X_{1:T})
```

Distribucional:

```math
p(X_{T+1:T+H}|X_{1:T})
```

A segunda formulação é superior quando múltiplos futuros são plausíveis.

---

# 3. Point-wise tokenization

Cada timestamp vira token/embedding:

```math
e_t=\phi(x_t)
```

Sequence length:

```math
N=T
```

Bom para granularidade fina; ruim para sequências longas.

---

# 4. Patch tokenization

Patch de comprimento $`P`$:

```math
p_i=[x_{iP},\ldots,x_{iP+P-1}]
```

Número de tokens:

```math
N\approx\frac{T}{P}
```

Trade-off:

```math
P\uparrow
\Rightarrow
SequenceLength\downarrow,
LocalResolution\downarrow
```

Patching é o equivalente temporal de reduzir resolução.

---

# 5. Multi-scale representation

Processos reais contêm frequências diferentes.

Uma representação hierárquica pode manter:

```math
X^{(0)},X^{(1)},\ldots,X^{(L)}
```

com:

```math
T_{l+1}<T_l
```

Fine scale captura spikes; coarse scale captura tendência/regime.

Zeus 2026 usa Transformer multiescala e hierarquia em U para equilibrar point fidelity e long-sequence efficiency.

---

# 6. Normalization

Uma série pode sofrer affine transform:

```math
x'_t=\frac{x_t-\mu}{\sigma}
```

ou normalization local/instance-wise.

Isso ajuda transfer entre séries de escala diferente, mas pode apagar significado absoluto quando magnitude é semanticamente importante.

### Regra

```math
Normalization\ choice\in Model\ Contract
```

não mero pré-processamento opcional.

---

# 7. Covariates

Contexto pode incluir:

```math
C_t=\{calendar,price,promotion,weather,static\ metadata,\ldots\}
```

Forecast real:

```math
p(Y_{future}|Y_{past},C_{past},C_{future-known})
```

Separar:

- observed covariates;
- known-future covariates;
- static features.

---

# 8. Deterministic forecasting

Loss MSE:

```math
\mathcal L_{MSE}=\frac1N\sum_i(y_i-\hat y_i)^2
```

Ótima para mean prediction sob hipóteses específicas.

Problema: comprime multimodalidade do futuro em média.

---

# 9. Quantile forecasting

Para quantile $`\tau`$:

Pinball loss:

```math
L_\tau(y,\hat q)
=
\max(\tau(y-\hat q),(\tau-1)(y-\hat q))
```

Gera intervalos:

```math
[q_{0.1},q_{0.5},q_{0.9}]
```

Coverage precisa ser calibrado no domínio.

---

# 10. Probabilistic forecasting

Modelo pode parametrizar distribuição:

```math
p(y|\theta_t)
```

ou gerar amostras:

```math
y^{(1)},\ldots,y^{(N)}\sim p_\theta
```

Metrics precisam avaliar distribuição, não só mean error.

---

# 11. CRPS

Continuous Ranked Probability Score mede distribuição predita versus observação.

Forma conceitual:

```math
CRPS(F,y)=\int_{-\infty}^{\infty}(F(z)-1[z\ge y])^2dz
```

Menor é melhor.

---

# 12. Autoregressive forecasting

```math
p(y_{T+1:T+H}|X)
=
\prod_{h=1}^{H}
p(y_{T+h}|X,y_{T+1:T+h-1})
```

Problema:

```math
Error_{h}\rightarrow Conditioning_{h+1}
```

acumulação de erro.

---

# 13. Direct / parallel forecasting

Prediz horizonte inteiro:

```math
\hat Y_{1:H}=f_\theta(X)
```

Evita AR error propagation, mas precisa modelar dependência interna do horizonte por outra forma.

---

# 14. Diffusion / flow time-series forecasting

Futuro como trajetória aleatória:

```math
Y_{future,\tau}
=\alpha_\tau Y_{future,0}+\sigma_\tau\epsilon
```

ou flow:

```math
\frac{dY_\tau}{d\tau}=v_\theta(Y_\tau,\tau,X_{past})
```

Útil para gerar **ensemble de futuros plausíveis**, especialmente em domínios multimodais.

Snapshot 2026: KiT aplica Diffusion Transformer + flow matching a trajetórias OHLCV financeiras.

---

# 15. Masked time-series modeling

Mascare intervalo $`M`$:

```math
\mathcal L=\sum_{t\in M}\ell(x_t,\hat x_t)
```

Variar o padrão de máscara pode induzir tarefas:

- extrapolation;
- interpolation;
- imputation;
- abstraction.

Zeus usa Multi-Objective Temporal Masking para unificar tarefas sem fine-tuning específico.

---

# 16. Imputation

Dado mask $`m_t`$:

```math
\hat x_t=f(X\odot m,m)
```

Missingness pode ser informativa:

```math
P(missing|state)\neq const
```

Logo preencher zero/mean sem mask explícita pode introduzir semântica falsa.

---

# 17. Anomaly detection

Possibilidades:

### Reconstruction residual

```math
e_t=|x_t-\hat x_t|
```

### Forecast surprise

```math
score_t=-\log p(x_t|x_{<t})
```

### Representation distance

```math
score_t=d(z_t,\mathcal M_{normal})
```

Threshold depende do regime e custo de falso positivo.

---

# 18. Classification

Converta série em representação global:

```math
z=Pool(f_\theta(X))
```

```math
P(y|X)=softmax(Wz)
```

Foundation model multi-task tenta tornar $`z`$ transferível entre domínios.

---

# 19. Regime shift

Processo muda:

```math
p_{train}(X,Y)\neq p_{deploy}(X,Y)
```

Em séries, drift pode ser:

- trend shift;
- volatility shift;
- seasonality shift;
- structural break;
- sensor recalibration.

Long context não corrige automaticamente regime antigo irrelevante.

---

# 20. Frequency domain

Transformada discreta:

```math
X_k=\sum_{n=0}^{N-1}x_n e^{-j2\pi kn/N}
```

Permite expor periodicidades, mas processos não estacionários podem exigir time-frequency/local methods.

Não elevar “decomposition” a requisito universal.

---

# 21. Failure surfaces em TSFM

- frequency aliasing;
- scale mismatch;
- irregular sampling;
- covariate leakage;
- future-known feature mal classificada;
- regime shift;
- persistence bias;
- horizon extrapolation collapse;
- underdispersed uncertainty;
- calibration failure;
- domain pretraining mismatch.

Estudos 2026 de causal stress-testing em TSFMs encontram falhas súbitas em padrões fora do regime pretraining; isso reforça que “foundation” não significa universal.

---

# PARTE B — TABULAR FOUNDATION MODELS

# 22. Estado tabular

Dataset supervisionado:

```math
D=\{(x_i,y_i)\}_{i=1}^{N}
```

```math
x_i=(x_{i1},\ldots,x_{iD})
```

Features podem ser:

- contínuas;
- categóricas;
- ordinais;
- timestamps;
- missing;
- strings/IDs.

Não existe necessariamente uma ordem natural das colunas.

---

# 23. Feature tokenization

Cada célula/feature pode gerar embedding:

```math
e_{ij}=Embed_j(x_{ij})
```

Pode incorporar column identity:

```math
e_{ij}=ValueEmbed(x_{ij})+ColumnEmbed(j)
```

Isso resolve parte da heterogeneidade.

---

# 24. Permutation considerations

Rows em supervised learning são usualmente exchangeable:

```math
P(D)=P(\pi(D))
```

para permutação $`\pi`$, salvo estrutura temporal/grupal explícita.

Columns não são exchangeable semanticamente a menos que identidade seja preservada.

Arquitetura precisa distinguir:

```math
Value\ identity\neq Feature\ identity
```

---

# 25. Missingness

Defina mask:

```math
m_{ij}=1[x_{ij}\ observed]
```

Modelo ideal recebe:

```math
(x_{ij},m_{ij})
```

Missing pode ser MCAR/MAR/MNAR; o mecanismo altera inferência.

---

# 26. Prior-data fitted networks — PFN intuition

TabPFN-style não é simplesmente “Transformer treinado em planilhas”.

Durante pretraining, modelo aprende sobre distribuições de tarefas/datasets sintéticos/priors:

```math
\theta^*=argmin E_{D\sim p(D)}L(f_\theta(D_{train},x^*),y^*)
```

Na inferência:

```math
P(y^*|D_{train},x^*)
```

é computado **in-context**, sem otimizar novos weights por dataset.

Isso lembra amortized Bayesian inference / meta-learning.

---

# 27. In-context supervised learning

Contexto contém pares:

```math
(x_1,y_1),\ldots,(x_N,y_N)
```

mais query:

```math
x^*
```

Modelo retorna:

```math
P(y^*|x^*,D)
```

O “prompt” é o próprio training set.

---

# 28. Dataset size as context budget

Diferente de LLM:

```math
Context\sim N\times D
```

crescimento de samples e features pressiona memória/attention.

TabPFN-2.5 amplia regime para dezenas de milhares de pontos e milhares de features, mas limites permanecem arquiteturalmente relevantes.

---

# 29. Classification vs regression

Classification:

```math
P(y=c|x,D)
```

Regression:

```math
p(y|x,D)
```

Regression exige modelar escala/caudas/heteroscedasticidade de forma que classification não exige.

---

# 30. Distillation to deployable model

Foundation model pode atuar como expensive teacher:

```math
F(D,x)\rightarrow \hat y
```

Distill para modelo menor:

```math
g_\phi(x)\approx F(D,x)
```

TabPFN-2.5 introduz caminho de distillation para MLP/tree ensemble, separando **training-time intelligence amortizada** de runtime barato.

---

# 31. Tabular metrics

Classification:

- accuracy;
- ROC-AUC;
- PR-AUC;
- log loss;
- Brier/calibration.

Regression:

- MAE;
- RMSE;
- R²;
- NLL/CRPS quando probabilístico.

Comparar modelos em múltiplos datasets exige ranks/aggregate robustos, não apenas média bruta.

---

# 32. Tabular failure surfaces

- dataset too large/wide for context;
- high-cardinality categorical explosion;
- leakage;
- feature semantics mismatch;
- missingness mechanism shift;
- covariate shift;
- target shift;
- calibration drift;
- extrapolation fora do suporte;
- IDs tratados como números ordinais;
- correlated rows violando exchangeability assumida.

---

# 33. Time series vs tabular — não fundir mentalmente

Time series:

```math
order\ matters
```

Tabular i.i.d. clássico:

```math
row\ order\ ideally\ irrelevant
```

Time series possui relógio e horizonte; tabular supervisionado possui training set/context.

Por isso dividimos o mesmo arquivo em duas metades, mas não tratamos como a mesma matemática.

---

# 34. Runtime

## Time series

Custo principal:

```math
N_{tokens}=f(T,patch,multiscale)
```

## Tabular PFN

Custo:

```math
N_{context}=f(N_{rows},D_{features},representation)
```

Em ambos, aumentar “dados de contexto” não altera weights, mas aumenta inferência.

Veja [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 35. Snapshot SOTA 2026

### Zeus

- tuning-free multi-task TSFM;
- point-wise tokenization;
- multiscale Transformer;
- Multi-Objective Temporal Masking;
- forecasting, probabilistic forecasting, imputation, anomaly, classification.

### TabPFN-2.5

- expansão substancial de dataset/feature regime;
- strong in-context tabular prediction;
- deployment distillation para MLP/tree ensembles.

### KiT

- flow-matching Diffusion Transformer para trajetórias financeiras futuras;
- exemplo de objetivo generativo contínuo aplicado a forecasting.

A mensagem importante: **time-series/tabular FMs estão divergindo arquiteturalmente, não convergindo para um simples “LLM de números”.**

---

# 36. Checklist TSFM

1. Point ou patch tokenization?
2. Qual sampling interval?
3. Normalization faz parte do recipe?
4. Há covariates future-known?
5. Forecast é point, quantile ou distributional?
6. AR ou parallel?
7. Qual horizon treinado/avaliado?
8. Como lida com missing/irregular sampling?
9. Qual regime shift esperado?
10. Forecast samples são calibrados?
11. Qual footprint por comprimento de série?

---

# 37. Checklist Tabular FM

1. Como continuous/categorical são representados?
2. Column identity está explícita?
3. Missing mask é usado?
4. Inference é in-context ou fine-tuned?
5. Qual limite de rows/features?
6. A ordem das rows importa para implementação?
7. Probabilidades são calibradas?
8. Há distillation para deploy?
9. Como trata high-cardinality categorical?
10. Há risco de leakage no contexto?

---

# Referências snapshot

- Zeus: Towards Tuning-Free Foundation Model for Time Series Analysis — https://proceedings.mlr.press/v306/fu26n.html
- TabPFN-2.5 — https://arxiv.org/abs/2511.08667
- KiT: Diffusion Transformer for financial time-series forecasting — https://arxiv.org/abs/2609.34507
- Causal Analysis for Time Series Foundation Models — https://arxiv.org/abs/2608.24303
