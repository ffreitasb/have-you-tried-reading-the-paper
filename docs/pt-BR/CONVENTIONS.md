---
title: Conventions & Maintenance Rules — Foundation Model Engineering Datasheets
aliases: [Datasheet Conventions, Editorial Conventions]
tags: [ai, referencia, governance, conventions, knowledge-management]
updated: 2026-10-01
---

# Conventions & Maintenance Rules

> Este arquivo governa **como a coleção cresce sem virar uma taxonomia inconsistente**.

---

# 1. Critério para criar um novo datasheet

Um novo arquivo de domínio só é justificado quando muda de forma material ao menos um destes eixos:

\[
\boxed{
Representation
\lor
Objective
\lor
InferenceTopology
\lor
StateDynamics
}
\]

Não criar arquivo separado apenas porque existe:

- novo produto;
- novo checkpoint;
- novo acrônimo;
- novo sampler;
- nova UI;
- nova técnica de adaptação.

Esses pertencem ao documento cujo mecanismo já cobre a novidade.

---

# 2. Estrutura canônica de um datasheet

Quando aplicável, seguir esta ordem:

1. **Scope & boundary**
2. **Canonical computational graph**
3. **Representation / state tensors**
4. **Governing equations**
5. **Architecture parameters**
6. **Training/objective parameters**
7. **Inference controls**
8. **Coupling matrix**
9. **Compute/memory model**
10. **Observables**
11. **Failure surfaces**
12. **Experimental protocol**
13. **Backend/tool mapping**
14. **Snapshot tecnológico datado**
15. **References**

Nem todo arquivo precisa de todas as seções, mas a ausência deve ser intencional.

---

# 3. Provenance tags

Usar as definições canônicas de [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

Tags principais:

```text
ARCH
MODEL
OBJ
DATA
TRAIN
ALIGN
PEFT
DISTILL
MERGE
GEN
INF
STATE
BACKEND
PIPE
INDEX
EVAL
SEC
UI
HEURISTIC
```

Uma variável pode ter mais de uma tag quando cruza camadas.

---

# 4. Níveis de afirmação

Toda frase técnica deve cair, implicitamente ou explicitamente, em uma destas classes:

## Identity / definition

Verdade por definição.

Exemplo:

\[
Recall@K=RelevantRetrieved@K/TotalRelevant
\]

## Architecture fact

Verdade para uma família/modelo específico.

Exemplo:

> determinado modelo usa GQA.

Exige fonte/snapshot quando contemporâneo.

## Approximation

Modelo útil de engenharia.

Exemplo:

\[
M_{KV}\approx2LTn_{kv}d_hbB
\]

Declarar hipóteses quando necessário.

## Empirical regularity

Comportamento observado em regimes comuns.

Exemplo:

> CFG muito alto frequentemente degrada imagem em determinada família.

## Heuristic

Recomendação operacional.

Deve ser claramente separada da matemática.

## Vendor/UI behavior

Só vale para produto/backend identificado.

---

# 5. Regra “phenomenology ≠ mechanism”

Dois knobs podem produzir percepção parecida sem serem equivalentes.

Exemplo:

\[
Temperature\neq CFG
\]

mesmo que ambos possam alterar percepção de “liberdade”.

Nunca converter analogia perceptual em equivalência matemática.

---

# 6. Símbolos

Símbolos são locais ao domínio quando houver colisão.

Regras:

- \(\mathcal L\) reservado para loss sempre que possível;
- \(\theta\) para learned parameters;
- \(B\) para batch;
- \(T\) para comprimento/tempo, sempre contextualizado;
- \(d\) para dimension;
- \(r\) para low-rank rank quando em PEFT;
- \(\eta\) para learning rate em training;
- \(\tau\) para contrastive/calibration temperature quando definido;
- \(s\) para CFG/guidance quando definido.

Ver colisões em [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

---

# 7. Tensor shapes

Sempre explicitar ordem quando shape importa.

Preferências:

## Sequência

\[
[B,T,d]
\]

## Imagem latente

\[
[B,C,H,W]
\]

## Vídeo

\[
[B,T,C,H,W]
\]

ou outra ordem **desde que declarada**.

Não assumir automaticamente convenção de framework.

---

# 8. Unidades

## Memória

Preferir GiB/MiB quando calculada em base binária.

\[
1GiB=2^{30}\ bytes
\]

## Storage comercial

GB/TB podem ser decimais quando reproduzindo especificação do fabricante.

## Bandwidth

Especificar GB/s ou GiB/s quando precisão importar.

## Tempo

ms/s.

## Throughput

Sempre nomear unidade:

- tokens/s;
- samples/s;
- frames/s;
- requests/s.

---

# 9. Snapshot policy

A coleção mistura dois tipos de conhecimento.

## Núcleo durável

Equações, definições, taxonomias.

Não devem depender da data.

## Snapshot tecnológico

- modelos atuais;
- backend features;
- library support;
- benchmarks ativos;
- specs/protocolos.

Sempre incluir data no cabeçalho global `updated:` e, quando necessário, na seção snapshot.

---

# 10. Source policy

Para claims contemporâneos, priorizar:

1. paper original;
2. documentação oficial;
3. repositório oficial;
4. standard/framework body;
5. survey confiável.

Evitar usar post secundário como fonte principal quando original existe.

---

# 11. Cross-link policy

Todos os arquivos vivem na raiz do mesmo diretório.

Usar Obsidian wikilinks sem `.md`:

```text
[02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
```

Não usar paths relativos enquanto todos permanecerem na raiz.

---

# 12. File naming

Datasheets numerados:

```text
NN_UPPER_SNAKE_CASE_DATASHEET.md
```

Exceções já estabelecidas devem manter o nome para não quebrar backlinks.

Arquivos meta não precisam de número:

```text
CONVENTIONS.md
CHANGELOG.md
```

---

# 13. Rename policy

Não renomear arquivo existente sem:

1. atualizar todos os wikilinks;
2. registrar no CHANGELOG;
3. idealmente manter alias/note de migração.

Knowledge management favorece estabilidade de identificadores.

---

# 14. Canonical parameter naming

Quando termo colide, usar nome qualificado:

- Sampling Temperature;
- Contrastive Temperature;
- Distillation Temperature.

Não usar um nome curto ambíguo em tabela transversal.

---

# 15. Backend-specific parameters

Registrar como:

```text
canonical concept → backend alias
```

Exemplo:

```text
Context Length → n_ctx / num_ctx / context_length
```

Não criar conceito novo para cada alias.

---

# 16. UI knobs

Toda variável de UI deve carregar `UI` até que o mapeamento seja conhecido.

Exemplo:

```text
"Creativity" [UI]
```

Somente após documentação:

```text
Creativity → temperature + top-p
```

se isso for realmente o que o produto faz.

---

# 17. Presets

Preset não pertence ao núcleo matemático.

Colocar em seção:

```text
Empirical operating points
```

com:

- modelo/família;
- backend;
- data;
- finalidade.

Nunca escrever “golden setup” universal.

---

# 18. Ranges

Separar:

1. **mathematical domain**;
2. **backend accepted range**;
3. **empirical useful range**.

Exemplo:

Sampling Temperature:

\[
T>0
\]

é domínio matemático.

Uma UI que limita `0..2` é implementação.

---

# 19. Reproducibility language

Nunca escrever:

> mesma seed = mesmo resultado

como lei universal.

Usar:

\[
Reproducibility
=f(
weights,
inputs,
seed,
dtype,
kernels,
backend,
hardware,
parallelism,
versions
)
\]

---

# 20. Physical cost

Sempre que parâmetro aumentar dimensão relevante, tentar mostrar impacto em:

- VRAM;
- RAM;
- bandwidth;
- FLOPs;
- latency;
- storage.

Exemplo:

\[
\frac{\partial M_{KV}}{\partial T}
\]

é mais útil que simplesmente “context aumenta VRAM”.

---

# 21. Coupling matrices

Quando possível, tabela deve explicitar:

```text
parameter ↑ → primary effect → secondary effect → failure surface
```

Não usar setas monotônicas quando relação é não-monotônica.

---

# 22. Observables

Toda seção de controles deveria, quando possível, apontar para variável mensurável.

Ideal:

\[
Control
\rightarrow StatePerturbation
\rightarrow Observable
\rightarrow Output
\]

Isso transforma tuning em experimento.

---

# 23. Evaluation policy

Toda recomendação comparativa importante deve poder ser testada conforme [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

Evitar:

- single-seed conclusion;
- benchmark score sem version;
- leaderboard sem system definition;
- subjective impression apresentada como fato.

---

# 24. Security policy

Nenhum prompt deve ser tratado como security boundary.

Security controls devem aparecer em:

- authn/authz;
- sandbox;
- validation;
- tool scope;
- runtime policy;
- logs/audit;
- rollback.

Veja [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

# 25. Deprecation

Conteúdo envelhecido não deve sumir sem explicação se for historicamente útil.

Marcar:

```text
LEGACY
MODEL-SPECIFIC
SUPERSEDED
```

Explicar por que deixou de ser universal.

---

# 26. Changelog discipline

Toda mudança estrutural deve entrar em [CHANGELOG](CHANGELOG.md).

Mudanças menores de typo não precisam de entrada individual.

Registrar:

- data;
- arquivos afetados;
- mudança conceitual;
- breaking rename, se houver.

---

# 27. Definition of done para novo datasheet

Antes de considerar final:

- [ ] scope definido;
- [ ] computational graph;
- [ ] representação/state;
- [ ] equações centrais;
- [ ] parâmetros classificados;
- [ ] custo físico quando relevante;
- [ ] observáveis;
- [ ] failure surfaces;
- [ ] cross-links;
- [ ] snapshot datado;
- [ ] referências;
- [ ] wikilinks válidos;
- [ ] fórmulas/fences balanceados.

---

# 28. Filosofia editorial

A coleção não deve responder apenas:

> “qual botão eu mexo?”

Ela deve permitir reconstruir:

\[
\boxed{
Architecture
\rightarrow
State
\rightarrow
Equation
\rightarrow
Control
\rightarrow
Observable
\rightarrow
Output
\rightarrow
Cost
}
\]

E, no lifecycle completo:

\[
\boxed{
Data
\rightarrow
Training
\rightarrow
Model
\rightarrow
Inference
\rightarrow
Evaluation
\rightarrow
Security/Monitoring
}
\]

Esse é o contrato epistemológico da coleção.
