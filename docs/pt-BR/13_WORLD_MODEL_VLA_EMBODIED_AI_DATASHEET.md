---
title: World Model / VLA / Embodied AI Datasheet v1.0
tags: [ai, world-model, vla, robotics, embodied-ai, control, policy, planning]
updated: 2026-10-01
---

# World Model / VLA / Embodied AI Datasheet v1.0

> Um agente digital escolhe chamadas de ferramenta. Um sistema embodied precisa escolher ações que **alteram um mundo dinâmico**, sob atraso, ruído, observação parcial e consequências físicas. World models aprendem o “plant”; VLAs aprendem uma policy multimodal sobre esse mundo.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md), [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md).

---

# 1. Tradução para engenharia de controle

Sistema clássico:

\[
x_{t+1}=f(x_t,u_t)+w_t
\]

\[
y_t=h(x_t)+v_t
\]

onde:

- \(x_t\): estado;
- \(u_t\): controle;
- \(y_t\): observação;
- \(w_t,v_t\): ruído.

World model aprendido:

\[
\hat x_{t+1}=f_\theta(\hat x_t,u_t)
\]

ou probabilístico:

\[
p_\theta(x_{t+1}|x_t,u_t)
\]

A analogia central:

\[
\boxed{World\ Model\approx Learned\ Plant\ Model}
\]

---

# 2. Model-free vs model-based policy

## Model-free

\[
a_t\sim\pi_\theta(a|o_t)
\]

Não exige explicitamente previsão do próximo estado.

## Model-based

\[
\hat s_{t+1}=f_\theta(s_t,a_t)
\]

A policy/planner pode imaginar consequências antes de agir.

---

# 3. Partial observability

Robô/agent raramente observa estado verdadeiro:

\[
o_t\sim p(o_t|s_t)
\]

Precisamos inferir belief/latent state:

\[
b_t=P(s_t|o_{1:t},a_{1:t-1})
\]

ou embedding recorrente:

\[
z_t=F(z_{t-1},o_t,a_{t-1})
\]

Isso aproxima POMDPs.

---

# 4. World model components

Arquitetura idealizada:

\[
o_t\xrightarrow{Encoder}z_t
\]

\[
(z_t,a_t)\xrightarrow{Dynamics}\hat z_{t+1}
\]

\[
\hat z_{t+1}\xrightarrow{Decoder}\hat o_{t+1}
\]

Opcionalmente:

\[
(z_t,a_t)\rightarrow \hat r_t
\]

\[
z_t\rightarrow \hat v_t
\]

---

# 5. Pixel-space vs latent world model

## Pixel-space

Prediz imagem/vídeo futuro:

\[
p(I_{t+1:t+H}|I_{\le t},a_{t:t+H})
\]

Prós:

- interpretável;
- fornece future visual evidence.

Contras:

- caro;
- precisa modelar detalhes perceptuais irrelevantes para controle.

## Latent-space

\[
z_{t+1}=f_\theta(z_t,a_t)
\]

Prós:

- compactação;
- foca features úteis.

Contras:

- latent pode esconder erro físico;
- difícil auditar.

---

# 6. Deterministic vs stochastic dynamics

Determinístico:

\[
\hat s_{t+1}=f_\theta(s_t,a_t)
\]

Probabilístico:

\[
s_{t+1}\sim p_\theta(s|s_t,a_t)
\]

Mundos reais têm múltiplos futuros plausíveis.

Quando incerteza importa, um único mean prediction pode ser perigoso:

\[
E[s_{t+1}]\notin feasible\ states
\]

em distribuições multimodais.

---

# 7. Multi-step rollout

\[
\hat s_{t+k}=f_\theta(\hat s_{t+k-1},a_{t+k-1})
\]

Erro recursivo:

\[
e_{t+k}\approx F(e_{t+k-1},model\ error)
\]

Quanto maior horizon:

\[
H\uparrow\Rightarrow accumulated\ model\ error\uparrow
\]

não necessariamente linearmente.

---

# 8. Planning / MPC analogy

Queremos:

\[
a^*_{t:t+H-1}
=
\arg\max_{a_{t:t+H-1}}
\sum_{k=0}^{H-1}\gamma^kR(\hat s_{t+k},a_{t+k})
\]

Executa-se tipicamente apenas a primeira ação e replaneja-se:

\[
MPC: plan\rightarrow act\rightarrow observe\rightarrow replan
\]

Essa é a ponte direta com controle preditivo.

---

# 9. Search over actions

## Sampling

Amostre \(N\) action sequences:

\[
A^{(1)},\ldots,A^{(N)}
\]

avalie retorno previsto:

\[
J(A^{(i)})
\]

escolha melhor.

## CEM-like optimization

Iterativamente atualize distribuição sobre ações a partir dos elites.

## Gradient planning

Se dynamics/reward são diferenciáveis:

\[
\nabla_AJ
\]

pode otimizar action sequence diretamente.

---

# 10. Vision-Language-Action — VLA

Entrada:

\[
C_t=
\{vision_t,language,state/proprioception_t,history\}
\]

Policy:

\[
a_t\sim\pi_\theta(a|C_t)
\]

VLA não é simplesmente VLM + botão de tool call: o action space pode ser contínuo, temporal e sujeito à dinâmica física.

---

# 11. Action representation

## Continuous

Exemplo manipulador:

\[
a_t=(\Delta x,\Delta y,\Delta z,\Delta r_x,\Delta r_y,\Delta r_z,g)
\]

## Discretized tokens

Cada dimensão é quantizada:

\[
a_t\rightarrow(token_1,\ldots,token_m)
\]

Permite usar autoregressive categorical decoder.

## Action chunks

\[
A_t=(a_t,a_{t+1},\ldots,a_{t+K-1})
\]

Reduz frequência de chamadas do backbone e pode suavizar controle.

---

# 12. Action chunking trade-off

Chunk maior:

\[
K\uparrow
\Rightarrow
InferenceFrequency\downarrow
\]

mas:

\[
FeedbackFrequency\downarrow
\]

Logo há trade-off entre throughput e closed-loop responsiveness.

Em engenharia:

> maior open-loop interval economiza compute, mas aumenta exposição a model mismatch/disturbance.

---

# 13. Autoregressive action policy

\[
P(A)=\prod_tp(a_t|a_{<t},C)
\]

Prós:

- compatível com Transformers causais;
- simples.

Contras:

- sequential latency;
- error propagation;
- ações contínuas exigem tokenização ou mixture outputs.

---

# 14. Diffusion policy

Noisy action trajectory:

\[
a_\tau=\alpha_\tau a_0+\sigma_\tau\epsilon
\]

Denoising condicionado à observação:

\[
a_{\tau}\rightarrow a_{\tau-1}\rightarrow\cdots\rightarrow a_0
\]

Vantagem: modelar distribuições multimodais de trajetórias contínuas.

Custo: múltiplos network evaluations.

---

# 15. Flow matching action policy

\[
\frac{da_\tau}{d\tau}=v_\theta(a_\tau,\tau,C)
\]

Permite gerar action trajectories via integração do campo vetorial.

WorldFly 2026 é exemplo de mecanismo dual-branch flow matching que gera previsão visual futura e ações de navegação de forma acoplada.

---

# 16. Joint world-action generation

Em vez de:

\[
WorldModel\rightarrow Planner
\]

podemos ter modelo acoplado:

\[
(C_t,noise)
\rightarrow
(\hat Video_{future},A_{future})
\]

A geração futura funciona como “imaginação” compartilhada com a policy.

Isso reduz separação modular, mas também torna debugging mais difícil.

---

# 17. Vision-language grounding for action

Instrução:

> “pegue a chave vermelha à direita”

exige:

\[
Language\rightarrow Object\ Identity
\]

\[
Vision\rightarrow Object\ Localization
\]

\[
Localization\rightarrow Reachable\ Pose
\]

\[
Pose\rightarrow Action\ Trajectory
\]

Um erro em qualquer estágio pode parecer “policy failure”.

---

# 18. State/action frequency

Controle possui relógio.

Se observation rate:

\[
f_o=30Hz
\]

e policy rate:

\[
f_\pi=5Hz
\]

cada decisão cobre aproximadamente:

\[
\frac{f_o}{f_\pi}=6
\]

frames de observação.

Latência total precisa satisfazer o regime dinâmico do sistema.

---

# 19. Latency budget

Closed-loop delay:

\[
T_{loop}
=T_{sense}+T_{encode}+T_{policy}+T_{decode}+T_{actuate}
\]

Se \(T_{loop}\) é grande em relação à constante de tempo do sistema, a policy opera com estado defasado.

A matemática de controle importa mais que “tokens/s”.

---

# 20. Safety envelope

Ação proposta:

\[
a_t^{raw}=\pi(s_t)
\]

Safety filter:

\[
a_t=\Pi_{\mathcal A_{safe}}(a_t^{raw})
\]

Pode incluir:

- joint limits;
- collision constraints;
- velocity/acceleration limits;
- workspace boundaries;
- human proximity;
- forbidden actions.

Uma policy segura não deve depender apenas de prompt.

---

# 21. Human in the loop vs supervisory control

HITL não precisa aprovar cada ação.

Pode atuar em nível supervisory:

\[
Human\rightarrow Goal/Mode/Constraint
\]

\[
Controller\rightarrow LowLevelActions
\]

Essa divisão é mais compatível com sistemas de alta frequência.

---

# 22. Sim-to-real gap

Treino em simulação:

\[
p_{sim}(s,a)
\]

Deploy:

\[
p_{real}(s,a)
\]

Se:

\[
p_{sim}\neq p_{real}
\]

policy sofre domain shift.

Técnicas:

- domain randomization;
- real-data fine-tuning;
- adaptation;
- robust control constraints.

---

# 23. World model error decomposition

## Perception error

\[
e_{enc}
\]

## Transition error

\[
e_{dyn}
\]

## Reward/value error

\[
e_R,e_V
\]

## Planning/search error

\[
e_{plan}
\]

## Actuation/model mismatch

\[
e_{act}
\]

Resultado:

\[
e_{task}=F(e_{enc},e_{dyn},e_R,e_{plan},e_{act})
\]

Trocar a policy não corrige automaticamente um encoder ruim.

---

# 24. Metrics

- success rate;
- episode return;
- collision rate;
- intervention rate;
- action latency;
- path efficiency;
- pose error;
- future prediction error;
- calibration/uncertainty;
- real-time factor;
- horizon before rollout divergence.

---

# 25. Failure surfaces

- hallucinated affordance;
- perception/action mismatch;
- temporal lag;
- compounding rollout error;
- action discretization artifacts;
- open-loop chunk muito longo;
- multimodal alignment failure;
- reward misspecification;
- sim-to-real shift;
- safety filter fighting policy;
- partial observability;
- multimodal future collapse.

---

# 26. Digital agent vs VLA

## Digital agent

\[
Action\in\{API,click,key,type,tool\}
\]

ambiente frequentemente transacional e observável via software.

## VLA

\[
Action\in\mathbb R^m\text{ ou trajectory}
\]

ambiente contínuo, ruidoso, parcialmente observável e irreversível em certos estados.

Veja [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) para a fronteira digital.

---

# 27. Snapshot SOTA 2026

Tendência central:

\[
World\ Model + VLA
\]

começa a convergir para modelos que **imaginam futuro perceptual e ação conjuntamente**.

WorldFly exemplifica flow matching acoplado para future video + navigation action em UAVs, justamente usando world modeling para lidar com oclusões e transições de viewpoint.

O insight de engenharia é mais amplo:

> um sistema embodied competente precisa modelar não apenas “o que fazer”, mas **como o mundo provavelmente responderá**.

---

# 28. Checklist de dissecação

1. Qual é a observação \(o_t\)?
2. Há estado latente/belief?
3. O modelo aprende transition dynamics?
4. O futuro é pixel ou latent?
5. O dynamics model é determinístico ou probabilístico?
6. Qual rollout horizon antes de divergir?
7. A policy é AR, diffusion ou flow?
8. Action space é contínuo ou tokenizado?
9. Gera ação única ou chunks?
10. Qual closed-loop frequency?
11. Qual end-to-end latency?
12. Existe planner separado?
13. Há hard safety layer?
14. Qual sim-to-real gap?
15. Como uncertainty entra na decisão?

---

# Referências snapshot

- WorldFly: A World-Model-Based Vision-Language-Action Model for UAV Navigation — https://arxiv.org/abs/2606.06147
