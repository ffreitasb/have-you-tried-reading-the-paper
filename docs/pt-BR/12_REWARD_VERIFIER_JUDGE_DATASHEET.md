---
title: Reward Model / Verifier / Judge Datasheet v1.0
tags: [ai, reward-model, verifier, judge, prm, orm, rlvr, evaluation]
updated: 2026-10-01
---

# Reward Model / Verifier / Judge Datasheet v1.0

> Geradores respondem “o que vem depois?”. Verificadores respondem “isso está correto/bom?”. Reward models aprendem um **campo escalar de preferência ou qualidade**; judges podem produzir score, ranking, crítica ou decisão.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md), [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

---

# 1. Quatro famílias que não devem ser confundidas

## 1.1 Scalar Reward Model

\[
r_\theta(x,y)\in\mathbb R
\]

Entrada: prompt/contexto \(x\) + resposta/ação \(y\).  
Saída: escalar.

---

## 1.2 Pairwise Preference Model

\[
P(y_A\succ y_B|x)
\]

Um score latente pode induzir preferência:

\[
P(A>B)=\sigma(r_A-r_B)
\]

---

## 1.3 Verifier

Decide propriedade verificável:

\[
V(x,y)\rightarrow\{0,1\}
\]

ou probabilidade:

\[
P(correct|x,y)
\]

Pode ser:

- rule-based;
- executable;
- learned;
- generative.

---

## 1.4 Judge

Sistema mais geral:

\[
J(x,y,criteria)\rightarrow score/rank/critique
\]

Pode ser um LLM generativo, não necessariamente um reward head especializado.

---

# 2. Bradley–Terry preference model

Se \(r_A,r_B\) são utilities:

\[
P(A>B)=
\frac{e^{r_A}}{e^{r_A}+e^{r_B}}
=
\sigma(r_A-r_B)
\]

Loss para par escolhido/rejeitado:

\[
\mathcal L
=
-\log\sigma(r_{chosen}-r_{rejected})
\]

O treinamento aprende **diferenças relativas**, não necessariamente uma escala absoluta calibrada.

---

# 3. Score ≠ probability

Um reward de `7.4` não significa 74% de chance de correção.

Para virar probabilidade confiável, precisamos de calibration:

\[
P(correct|r)
\]

estimada/validada separadamente.

Possíveis técnicas:

- Platt/logistic scaling;
- isotonic regression;
- temperature scaling;
- binning/calibration curves.

---

# 4. Outcome Reward Model — ORM

Avalia a resposta final:

\[
R_{outcome}=R(x,y_{final})
\]

Vantagem:

- barato;
- labeling mais simples;
- bom quando resultado é verificável.

Limitação:

- não distingue onde a trajetória errou;
- pode premiar solução correta por raciocínio espúrio.

---

# 5. Process Reward Model — PRM

Avalia passos intermediários:

\[
r_t=R(x,y_{1:t})
\]

ou transições:

\[
r_t=R(s_t,a_t,s_{t+1})
\]

Isso permite:

- detectar erro cedo;
- podar search;
- supervisionar agentes;
- fornecer reward denso.

### Custo

Se cada passo exige avaliação:

\[
C_{PRM}\propto N_{steps}\times C_{verifier}
\]

Process supervision pode melhorar observabilidade mas custa muito mais inferência/anotação.

---

# 6. Bidirectional / lookahead process evaluation

Avaliar um passo apenas pelo prefixo pode ser ambíguo:

\[
P(correct\ step|prefix)
\]

Pode-se incorporar informação de continuação/outcome:

\[
P(step\ valid|prefix,suffix/outcome)
\]

Isso reduz miopia, mas introduz leakage se usado incorretamente em setting online.

---

# 7. Generative verifier

Em vez de scalar head:

\[
(x,y)
\rightarrow
LLM
\rightarrow
analysis/critique
\rightarrow
verdict
\]

Pode usar ferramentas/ambiente:

\[
Verifier
\rightarrow Tool
\rightarrow Evidence
\rightarrow Verdict
\]

Em 2026 aparecem PRMs generativos environment-aware justamente para detectar erros silenciosos que não aparecem como exceção.

### Trade-off

\[
VerifierCapability\uparrow
\leftrightarrow
Latency/Cost/Variance\uparrow
\]

---

# 8. Rule-based verifier

Quando existe checker determinístico:

\[
V(y)=1[y\in\mathcal S_{valid}]
\]

Exemplos:

- compilação;
- unit tests;
- symbolic equivalence;
- schema validation;
- game outcome;
- constraint solver.

Essa classe fornece reward de alta precisão **no domínio coberto**, mas pode ser estreita.

---

# 9. RL with Verifiable Rewards — RLVR

Policy:

\[
y\sim\pi_\theta(y|x)
\]

Verifier:

\[
r=V(x,y)
\]

RL otimiza:

\[
\max_\theta E_{y\sim\pi_\theta}[r]
\]

O gargalo passa a ser a cobertura do verifier.

Generative verifiers ampliam domínios, mas trocam certeza determinística por erro/calibration de modelo.

---

# 10. LLM-as-a-Judge

Prompt de avaliação:

\[
J(prompt,response,rubric)\rightarrow judgment
\]

Saídas:

- scalar 1–10;
- binary pass/fail;
- pairwise preference;
- categorical rubric;
- structured JSON;
- critique textual.

### Importante

O judge é outro modelo com seus próprios priors.

\[
JudgeError\neq0
\]

---

# 11. Pairwise judging

Dado A/B:

\[
J(x,A,B)\rightarrow A>B\text{ ou }B>A
\]

Vantagem: comparações relativas costumam ser cognitivamente mais fáceis que score absoluto.

Problema: **position bias**.

Teste de swap:

\[
J(x,A,B)\stackrel{?}{=}inverse(J(x,B,A))
\]

Se não, há instabilidade posicional.

---

# 12. Judge biases

## Position bias

Preferência por primeira/segunda opção.

## Verbosity bias

\[
P(win|longer) > P(win|quality\ equivalent)
\]

## Style bias

Markdown, assertividade, fórmulas ou tom podem alterar score sem alterar correção.

## Self-preference

Modelo pode favorecer outputs parecidos com seu próprio estilo/distribuição.

## Reference anchoring

Uma referência defeituosa pode induzir judge ao erro.

---

# 13. Calibration

Se judge retorna confiança \(p_i\):

Calibration ideal:

\[
P(correct|p=0.8)\approx0.8
\]

### Brier score

\[
BS=\frac1N\sum_i(p_i-y_i)^2
\]

### Expected Calibration Error

\[
ECE=\sum_b\frac{|B_b|}{N}
|acc(B_b)-conf(B_b)|
\]

Accuracy alta não implica calibration boa.

---

# 14. Bias-corrected evaluation

Se judge tem sensibilidade/especificidade imperfeitas, raw judge rate pode ser estimador enviesado do desempenho real.

Conceitualmente:

\[
ObservedScore
=F(TrueQuality,JudgeQuality,Calibration)
\]

Quando judge quality muda entre modelos/domínios, comparar scores diretamente pode inverter conclusões.

Logo a pergunta SOTA++ não é só:

> “qual judge é melhor?”

mas:

> “qual é a estabilidade da função de erro/calibration do judge neste domínio?”

---

# 15. Best-of-N

Gerador produz:

\[
Y=\{y_1,\ldots,y_N\}
\]

Verifier escolhe:

\[
y^*=\arg\max_iR(x,y_i)
\]

Se probabilidade de produzir pelo menos uma solução boa cresce com \(N\), verifier converte compute em qualidade.

Mas:

\[
Quality_{selected}
\le
Quality_{oracle-best}
\]

conforme erro do verifier.

---

# 16. Selection economics

Custo aproximado:

\[
C_{total}
=N\cdot C_{generation}
+N\cdot C_{verification}
\]

Se verifier é generativo grande, seleção pode custar tanto quanto geração.

Avaliar ganho marginal:

\[
\frac{\Delta Quality}{\Delta Compute}
\]

---

# 17. Majority voting / self-consistency

Para respostas discretas:

\[
\hat y=mode(y_1,\ldots,y_N)
\]

Funciona quando erros são suficientemente independentes.

Se outputs compartilham viés sistemático:

\[
Corr(error_i,error_j)\uparrow
\Rightarrow
benefit\downarrow
\]

Diversidade do ensemble importa.

---

# 18. Hidden-state verification

Verificação não precisa ler apenas texto final.

Se reasoning trace possui hidden states:

\[
h_{start},h_{end}
\]

pode-se definir:

\[
\Delta h=h_{end}-h_{start}
\]

e classificar trajetória por geometria interna.

Trabalho ACL 2026 mostra que trajetórias corretas/incorretas podem exibir diferenças geométricas úteis para seleção sem treinar reward model adicional.

Isso expande “verifier” para além de surface text.

---

# 19. Rubric-augmented judging

Rubric:

\[
R=\{criterion_1,\ldots,criterion_m\}
\]

Judge pode decompor:

\[
score(y)=\sum_iw_i score_i(y)
\]

Vantagem: auditabilidade.

Risco: rubric ruim cria **structured misguidance** — um critério incorreto passa a orientar consistentemente o modelo para a decisão errada.

---

# 20. Reward hacking

Policy otimiza proxy:

\[
\max R_{proxy}
\]

mas queremos:

\[
\max U_{true}
\]

Se:

\[
R_{proxy}\neq U_{true}
\]

policy pode explorar falhas.

Goodhart:

> quando a medida vira alvo, sua relação com o objetivo real pode degradar.

---

# 21. Overoptimization

Mesmo reward model razoável pode falhar fora da distribuição quando policy é empurrada para extremos:

\[
\pi_{new}\gg\pi_{training\ distribution}
\]

Quanto mais forte a otimização contra um RM imperfeito, maior o risco de explorar zonas não calibradas.

---

# 22. Verifier-guided search

Árvore de raciocínio:

\[
s_0\rightarrow\{s_1^1,\ldots,s_1^k\}
\]

PRM/verifier pontua:

\[
R(s_t^i)
\]

Beam/search preserva top candidatos.

Trade-off:

\[
BranchingFactor\uparrow
\Rightarrow
SearchCoverage\uparrow,
Compute\uparrow
\]

---

# 23. Código: executor como verifier

No domínio de código:

\[
code\rightarrow compiler/tests\rightarrow result
\]

Esse é um verifier externo excelente para propriedades cobertas.

Mas:

\[
TestsPass\not\Rightarrow ProgramCorrect\ universally
\]

Cobertura dos testes limita a evidência.

Veja [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md).

---

# 24. Agentes: process reward + environment

Para trajetória:

\[
\tau=(s_0,a_0,s_1,a_1,\ldots)
\]

PRM environment-aware pode verificar:

- se ação observou evidência;
- se estado mudou como esperado;
- se erro foi recuperável;
- se ferramenta foi usada corretamente.

Isso aproxima avaliação de sistemas de controle, não apenas de texto.

---

# 25. Metrics

## Pairwise accuracy

\[
Acc=\frac{correct\ preferences}{total}
\]

## Kendall \(\tau\)

Correlação ordinal.

## Spearman \(\rho\)

Correlação de ranks.

## Calibration

ECE/Brier/reliability diagram.

## Agreement

Cohen's kappa ou equivalentes quando adequado.

Não use uma métrica única para tudo.

---

# 26. Failure surfaces

- reward model domain shift;
- preference inconsistency;
- label noise;
- verbosity/style bias;
- position bias;
- reference error;
- calibration drift;
- reward hacking;
- overoptimization;
- correlated verifier/generator error;
- hidden rubric assumptions;
- process reward penalizando exploração legítima.

---

# 27. Snapshot SOTA 2026

Tendências relevantes:

- PRMs deixam de ser apenas math-step scorers e passam a interagir com ambiente;
- generative verifiers ampliam RLVR para domínios sem checker trivial;
- hidden-state trajectories começam a ser exploradas como sinal de correctness;
- judge calibration/bias é tratada como problema estatístico explícito;
- rubric-augmented reward modeling busca decompor “qualidade” em critérios mais auditáveis.

---

# 28. Checklist para qualquer evaluator

1. É score, probability, rank ou critique?
2. A escala é calibrada?
3. Treinou pairwise ou pointwise?
4. Avalia outcome ou processo?
5. Usa evidência externa?
6. Há checker determinístico disponível?
7. Qual o domain shift?
8. Existe position/verbosity/style bias?
9. Swap test foi feito?
10. Qual o custo por candidato?
11. O gerador e judge compartilham viés/model family?
12. O reward pode ser explorado?
13. Qual métrica valida agreement/calibration?
14. Best-of-N melhora devido ao gerador ou ao seletor?

---

# Referências snapshot

- DataPRM / Process-Level Reward Modeling for Agentic Data Analysis — https://arxiv.org/abs/2604.24198
- Your Reasoning Model is Secretly a Reward Model — https://aclanthology.org/2026.acl-long.788/
- Bias and Uncertainty in LLM-as-a-Judge Estimation — https://arxiv.org/abs/2605.06939
- C2: Rubric-Augmented Reward Modeling — https://aclanthology.org/2026.acl-long.523/
- The Bidirectional Process Reward Model — https://aclanthology.org/2026.acl-long.572/
- Crossing the Reward Bridge / generative verifier RLVR — https://aclanthology.org/2026.acl-long.178/
