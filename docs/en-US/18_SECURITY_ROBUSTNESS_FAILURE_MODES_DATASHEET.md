---
title: Security, Robustness & Failure Modes Datasheet — SOTA++ 2026
aliases: [AI Security Datasheet, Robustness Datasheet, Failure Modes Datasheet]
tags: [ai, reference, security, robustness, red-teaming, prompt-injection, agent-security, supply-chain]
updated: 2026-10-01
---

# Security, Robustness & Failure Modes Datasheet — SOTA++ 2026

> In probabilistic systems, failure is not a rare exception; it is part of the operating surface. Security begins when the system assumes that **the model, context, retrieved data, tools, and external artifacts can all be wrong or hostile**.

The fundamental distinction is:

\[
\boxed{
Safety \neq Security \neq Robustness \neq Reliability
}
\]

- **Safety**: prevent harm even when there is no attacker.
- **Security**: resist an intentional adversary.
- **Robustness**: preserve behavior under perturbation or distribution shift.
- **Reliability**: perform the intended function at an acceptable failure rate.

See also:

- [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md)
- [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)

---

# 1. Threat model first, mitigation second

A threat model should answer:

1. **Asset** — what are we protecting?
2. **Adversary** — who can attack?
3. **Entry point** — where can input enter?
4. **Trust boundary** — where does data stop being trusted?
5. **Capability** — what can the system do?
6. **Impact** — what happens if it fails?

Without a threat model, “security” becomes a disconnected checklist of good practices.

---

# 2. The trust graph

A modern system can be viewed as:

```text
user
  ↓
prompt / files / media
  ↓
model
  ↔ memory
  ↔ retrieval corpus
  ↔ MCP/tools/APIs
  ↔ external web/services
  ↓
actions / generated output
  ↓
downstream interpreters / humans / systems
```

Every arrow is a **trust boundary**.

---

# 3. Principle zero: the model is an untrusted component

Even without an attacker:

\[
P(ModelError)>0
\]

With an adversary:

\[
P(ModelError|AdversarialInput)
>
P(ModelError|NominalInput)
\]

Therefore model output should be treated as **untrusted data** until validated for the specific operation.

---

# 4. Prompt injection — the structural problem

In LLM systems, data and instructions share the same semantic channel.

If:

\[
Context = TrustedInstruction + UntrustedContent
\]

then the model has to infer which text is allowed to control behavior.

There is no privilege separation analogous to CPU ring levels inside the token stream.

That makes prompt injection an **instruction/data boundary** failure.

---

# 5. Direct prompt injection

The attacker explicitly supplies adversarial instructions:

```text
ignore previous instructions...
```

The defense cannot be merely “tell the model to ignore attacks.”

Controls must also exist outside the model:

- capability restriction;
- input/output validation;
- least privilege;
- approval gates;
- isolation.

---

# 6. Indirect prompt injection

Hostile content arrives through an external source:

```text
web page
email
PDF
retrieved document
issue/comment
tool output
```

Pipeline:

\[
ExternalContent
\rightarrow Context
\rightarrow Model
\rightarrow Action
\]

The user may never have seen the adversarial instruction.

---

# 7. Prompt injection is not the same as jailbreaking

## Prompt injection

An attacker attempts to alter the system's **control flow**.

## Jailbreak

Attempts to bypass model policy or behavioral restrictions.

There is overlap, but the threat models are different.

---

# 8. The system prompt is not a secret store

A system prompt can be:

- inferred;
- partially extracted;
- exposed through tool traces;
- reconstructed from behavior.

Do not store:

- API keys;
- passwords;
- privileged tokens;
- infrastructure secrets.

inside it.

\[
PromptVisibilityAssumption\neq SecurityBoundary
\]

---

# 9. Sensitive information disclosure

Possible sources include:

- context;
- retrieval;
- memory;
- logs;
- training memorization;
- tool output;
- environment variables carrying secrets.

Controls should operate both before and after the model.

---

# 10. Training-data poisoning

An attacker alters the training distribution:

\[
D' = D \cup D_{poison}
\]

to induce:

- backdoors;
- targeted behavior;
- degraded accuracy;
- misinformation.

A small fraction of strategically chosen data can have a disproportionate effect.

---

# 11. Backdoors

The attacker wants normal behavior on the standard distribution:

\[
f(x)=normal
\]

but malicious behavior under a trigger:

\[
f(x\oplus trigger)=malicious
\]

Triggers may be:

- tokens;
- phrases;
- visual patterns;
- audio;
- metadata;
- multimodal combinations.

---

# 12. Fine-tuning poisoning

PEFT does not remove the risk.

A small adapter can change behavior in a targeted way:

\[
W'=W+\Delta W_{adapter}
\]

From a supply-chain perspective, an adapter is **behavioral code executed through parameters**.

---

# 13. Model supply chain

Possible artifacts include:

- `.safetensors`;
- `.gguf`;
- PyTorch pickle/checkpoints;
- tokenizer files;
- Python model code;
- custom ops;
- LoRA/adapters;
- ComfyUI nodes;
- wheels/packages.

Do not confuse:

\[
ModelFile
\]

with:

\[
SafeToLoad
\]

---

# 14. Serialization risk

Pickle-based formats can execute code during deserialization when loaded from a hostile source.

`safetensors` was designed to store tensors without arbitrary code execution during deserialization.

That removes one class of risk; it does not guarantee model integrity.

A `.safetensors` file can still contain maliciously trained weights.

---

# 15. GGUF

GGUF is a binary weight/metadata format for ggml/llama.cpp-like runtimes, not an arbitrary Python pickle.

However:

- parser bugs are still possible;
- metadata can be hostile;
- the model can be backdoored;
- source and hash still matter.

\[
NonExecutableFormat\neq TrustedArtifact
\]

---

# 16. `trust_remote_code`

Allowing remote repository code means:

\[
ModelRepository
\rightarrow PythonExecution
\]

The trust boundary changes completely.

Use it only when:

- the source is trusted;
- the code is reviewed/pinned;
- the environment is isolated.

---

# 17. Custom nodes — ComfyUI

A custom node is often Python code with access to the process, filesystem, and network.

Therefore:

\[
InstallCustomNode
\approx
InstallSoftware
\]

not:

\[
InstallCustomNode
\approx
LoadModel
\]

The threat surface includes:

- install scripts;
- dependencies;
- arbitrary shell/network access.

---

# 18. Dependency supply chain

Risks include:

- typosquatting;
- dependency confusion;
- compromised maintainers;
- malicious updates;
- transitive dependencies;
- compromised binary wheels.

Controls:

- pinning;
- hashes;
- lockfiles;
- isolated environments;
- minimal dependencies;
- provenance/signatures where available.

---

# 19. RAG poisoning

An attacker modifies the corpus:

\[
D_{retrieval}'=D\cup Poison
\]

If the poison ranks highly:

\[
P(Poison\in TopK)\uparrow
\]

then contaminated context reaches the model.

This combines:

- retrieval attack;
- prompt injection;
- misinformation.

See [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 20. Embedding/vector weaknesses

Attacks may exploit:

- embedding collisions;
- nearest-neighbor manipulation;
- malicious chunk placement;
- metadata-filter bypass;
- cross-tenant vector-store leakage.

Similarity does not imply trust:

\[
HighCosineSimilarity
\not\Rightarrow
TrustedDocument
\]

---

# 21. Retrieval authorization

Applying authorization **after** content has been retrieved may already be too late.

Ideally:

\[
CandidateSet
=
Documents(user\ is\ authorized\ to\ access)
\]

before ranking and context injection.

---

# 22. Agent attack surface

An agent adds action to the system:

\[
Observe\rightarrow Decide\rightarrow Act
\]

Failure is no longer limited to incorrect text.

It can modify external state.

---

# 23. Excessive agency

Risk grows across three dimensions:

\[
Risk
\propto
Functionality
\times Permissions
\times Autonomy
\]

Reducing any one factor reduces blast radius.

OWASP has formalized this class across multiple versions and expanded the agentic treatment in 2025–2026.

---

# 24. Least privilege

Agent permissions should satisfy:

\[
Permissions_{agent}
\subseteq
Permissions_{minimum\ required}
\]

Avoid giving a globally privileged credential to a narrow read-only task.

---

# 25. Capability design

Prefer a narrow tool:

```text
read_invoice(invoice_id)
```

over:

```text
execute_sql(query)
```

or:

```text
run_shell(command)
```

The more open-ended the interface:

\[
AttackSurface\uparrow
\]

---

# 26. Authorization outside the model

The model may propose:

\[
action=(tool,args)
\]

But a policy engine should decide:

\[
Allowed(user,action,state)?
\]

Authorization should not depend on “the model sounded confident.”

---

# 27. Human-in-the-loop

HITL should be risk-based rather than required for every event.

A useful decision function is:

\[
RequireApproval
=
I(
Impact\times Irreversibility\times Uncertainty
>\tau
)
\]

The approval surface should show:

- the concrete action;
- the target;
- the arguments;
- the expected effect;
- irreversibility.

---

# 28. Human approval is not an absolute defense

Humans are vulnerable to:

- automation bias;
- fatigue;
- trust exploitation;
- misleading explanations.

The OWASP Agentic Top 10 explicitly calls out Human-Agent Trust Exploitation.

---

# 29. Agent goal hijack

An attacker alters the agent's operational objective through:

- prompt injection;
- poisoned memory;
- poisoned tool output;
- malicious peer agents.

The goal state must be protected or separated from untrusted content.

---

# 30. Tool misuse

A legitimate tool plus malicious arguments yields:

\[
SafeTool
+
UnsafeInvocation
=
UnsafeSystem
\]

Validate parameters semantically, not just against a JSON schema.

---

# 31. Identity & privilege abuse

In agentic systems, identity should be:

- explicit;
- scoped;
- short-lived where possible;
- attributable.

Avoid a shared superuser identity.

---

# 32. Agentic supply chain

An MCP server or tool provider may change after approval.

Runtime discovery increases risk:

\[
DynamicComponents
\rightarrow
DynamicTrustGraph
\]

Pinning/allowlisting, metadata validation, and policy enforcement become necessary.

---

# 33. Unexpected code execution

Natural-language agents can transform output into:

- shell;
- SQL;
- Python;
- templates;
- browser scripts.

Every downstream interpreter reintroduces classic injection risk.

---

# 34. Memory/context poisoning

If persistent memory accepts adversarial content:

\[
attack_t
\rightarrow Memory
\rightarrow behavior_{t+n}
\]

then the attack survives the original session.

Memory needs:

- provenance;
- write policy;
- expiration;
- review;
- scope.

---

# 35. Inter-agent communication

Messages between agents should be treated as untrusted input.

Signing or identifying the source helps establish authenticity, but does not guarantee semantic correctness.

\[
AuthenticatedMessage\neq SafeInstruction
\]

---

# 36. Cascading failures

If agents depend on one another:

\[
Error_A
\rightarrow
State_B
\rightarrow
Error_B
\rightarrow\cdots
\]

blast radius grows with coupling.

Controls include:

- circuit breakers;
- rate limits;
- independent validation;
- bounded retries;
- transactional steps.

---

# 37. Rogue / policy-divergent agents

There is no need to anthropomorphize.

Operationally, it means:

\[
ObservedPolicy
\notin
AllowedPolicyEnvelope
\]

regardless of the model's supposed “intent.”

Monitor behavior, not psychology.

---

# 38. Agent Control Standard — 2026

The OWASP ACS, released in September 2026, emphasizes agents that are:

- inspectable;
- traceable;
- instrumentable;
- controllable at runtime.

The correct architecture is:

\[
AgentDecision
\rightarrow
PolicyHook
\rightarrow
Allow/Transform/Deny
\rightarrow
Execution
\]

not:

\[
AgentDecision\rightarrow Execution
\]

---

# 39. Output handling

Model output may flow into:

- HTML;
- Markdown renderers;
- shell;
- SQL;
- filesystem paths;
- APIs;
- email;
- browsers.

Never confuse natural-language generation with sanitization.

---

# 40. Structured output helps syntax, not intent

Grammar/schema can guarantee:

\[
y\in\mathcal L(Schema)
\]

It does not guarantee:

\[
SemanticallySafe(y)
\]

Valid JSON can still request:

```json
{"action":"delete","target":"production"}
```

---

# 41. Idempotency

A critical operation should, where semantically possible, prefer:

\[
f(f(s,a),a)=f(s,a)
\]

Then retries do not multiply side effects.

---

# 42. Transactionality

Group operations:

\[
BEGIN
\rightarrow actions
\rightarrow validation
\rightarrow COMMIT/ROLLBACK
\]

For agents, rollback is an extremely valuable safety/security mechanism.

---

# 43. Bounded retries

Infinite retries are a failure amplifier.

\[
N_{retry}\le N_{max}
\]

Add:

- backoff;
- error classification;
- stop conditions;
- escalation.

---

# 44. Resource exhaustion / unbounded consumption

An attacker or defective loop can trigger:

- huge context;
- infinite tool loops;
- massive image/video resolution;
- enormous batch sizes;
- recursive agent spawning.

Define budgets:

\[
Tokens\le T_{max}
\]

\[
ToolCalls\le C_{max}
\]

\[
WallTime\le t_{max}
\]

\[
Cost\le \$_{max}
\]

---

# 45. Model denial of service

Pathological inputs can amplify compute/memory demand.

LLM example:

\[
ContextLength\uparrow
\Rightarrow
KV\uparrow
\]

Video example:

\[
T\times H\times W\uparrow
\Rightarrow
Compute/Memory\uparrow\uparrow
\]

See [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---
# 46. Adversarial robustness

Perturbation:

\[
x'=x+\delta
\]

with:

\[
\|\delta\|\le\epsilon
\]

Robustness seeks:

\[
f(x')\approx f(x)
\]

for semantically irrelevant perturbations.

---

# 47. Discrete adversarial space

In text, \(\delta\) is not simply continuous noise.

It may be:

- typos;
- homoglyphs;
- Unicode;
- paraphrases;
- token-boundary attacks;
- whitespace;
- prompt restructuring.

The distance measure must be semantically appropriate.

---

# 48. Multimodal adversarial input

An attack may exist only in the image/audio channel while the text looks benign.

\[
Input=(Text,Image)
\]

with:

\[
Text=safe
\]

but:

\[
Image=adversarial
\]

VLM security has to evaluate every modality.

---

# 49. OOD / distribution shift

Training:

\[
x\sim P_{train}
\]

Deployment:

\[
x\sim P_{deploy}
\]

If:

\[
P_{deploy}\neq P_{train}
\]

performance may degrade without any attacker at all.

That is a robustness/reliability problem, not necessarily a security problem.

---

# 50. Calibration under shift

A model may retain reasonable accuracy while losing calibration:

\[
Confidence\not\approx CorrectnessProbability
\]

under domain shift.

Risk-based systems should monitor calibration drift.

---

# 51. Hallucination as a failure mode

Hallucination is output unsupported by the relevant state/evidence.

It is not a standalone vulnerability, but it can become exploitable when downstream systems trust it automatically.

\[
Hallucination
+ExcessiveAgency
\rightarrow
OperationalIncident
\]

---

# 52. Retrieval grounding does not eliminate hallucination

Even with correct documents:

- retrieval can fail;
- context can be ignored;
- synthesis can be wrong;
- documents can contradict one another.

\[
RAG\neq TruthOracle
\]

---

# 53. Verifier correlation risk

If generator and verifier share the same error:

\[
P(V accepts\ wrong\ output)
\]

can remain high.

Architectural diversity and external evidence reduce correlated error.

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 54. Privacy attacks

Relevant classes include:

- membership inference;
- model inversion;
- memorization extraction;
- prompt/context exfiltration;
- vector-store leakage;
- logging leaks.

Privacy is not guaranteed merely because the AI runs locally if logs and context remain exposed.

---

# 55. Membership inference

The question is:

\[
Was\ x\in D_{train}?
\]

An attacker exploits statistical differences in behavior/confidence.

Risk depends on:

- overfitting;
- data rarity;
- access level;
- model exposure.

---

# 56. Model extraction / theft

Goals include:

- copying behavior;
- partially reconstructing weights;
- inferring proprietary prompts/data.

Controls:

- access control;
- rate limiting;
- anomaly detection;
- watermarking/provenance as supporting signals, not as the sole defense.

---

# 57. Local AI security — advantages and illusions

Running locally reduces some data flows to third parties.

But it introduces:

- model downloads;
- community binaries;
- custom nodes;
- local API servers;
- web UIs;
- exposed ports;
- weak authentication.

\[
Local\neq SecureByDefault
\]

---

# 58. Localhost is not a trust boundary

A service bound to:

```text
127.0.0.1:PORT
```

may still be reachable by malicious local processes or, depending on configuration/CORS/authentication, browser-based attack patterns.

Use binding and authentication deliberately.

---

# 59. Model-server exposure

If an Ollama/LM Studio/KoboldCpp/API server is exposed to LAN/WAN, verify:

- authentication;
- TLS;
- bind address;
- CORS;
- rate limits;
- file/tool capabilities;
- reverse-proxy policy.

Do not expose it because “it's only inference.”

---

# 60. ComfyUI-specific risk model

Separate:

## Model files

weights/checkpoints.

## Workflows

may reference paths/nodes.

## Custom nodes

execute Python.

## Manager/installers

download software/dependencies.

The largest risk is often not the `.safetensors` file, but the executable ecosystem around it.

---

# 61. SillyTavern/tool-extension risk

Extensions/scripts may access:

- frontend context;
- endpoints;
- local storage;
- external services.

Treat installing an extension as a software supply-chain event.

---

# 62. Integrity via hashing

For an artifact:

\[
h=SHA256(file)
\]

Hash pinning lets you detect changes.

But a hash does not answer:

> “was this artifact trustworthy in the first place?”

It proves identity, not benignity.

---

# 63. Provenance manifest

Record:

```yaml
artifact:
  source: ...
  repo_revision: ...
  filename: ...
  sha256: ...
  license: ...
  remote_code: false
  custom_ops: false
  reviewed: ...
```

Especially for models, nodes, and adapters.

---

# 64. Sandbox

Principle:

\[
Compromise(component)
\not\Rightarrow
Compromise(host)
\]

Use isolation mechanisms such as:

- containers;
- VMs;
- restricted filesystem access;
- network policy;
- low-privilege users.

The more agentic/code-executing the system is, the more valuable the sandbox becomes.

---

# 65. Network egress control

If an agent does not need the internet:

\[
Egress=deny
\]

If it needs only specific hosts:

\[
Egress\subset Allowlist
\]

This reduces exfiltration blast radius.

---

# 66. Secret management

Never pass a secret to the model unless it is actually necessary.

The tool should inject credentials internally:

```text
model → call tool(action)
tool → inject secret outside model context
```

instead of:

```text
secret → prompt → model → tool
```

---

# 67. Logs as an attack surface

Logs may contain:

- prompts;
- private documents;
- tokens;
- tool arguments;
- credentials accidentally returned by downstream systems.

Define:

- retention;
- redaction;
- access control;
- encryption;
- sampling.

---

# 68. Security observability

Capture structured events:

\[
Event=(actor,action,target,result,policy,trace_id,time)
\]

For agents, auditability depends on a complete action trace.

---

# 69. Detection versus prevention

No control is perfect.

Layers:

## Prevent

block the action.

## Detect

identify suspicious behavior.

## Contain

limit blast radius.

## Recover

rollback/revoke/rebuild.

Defense in depth:

\[
Risk_{residual}
\approx
Risk_0
\prod_i(1-E_i)
\]

only as intuition; controls are not independent in practice.

---

# 70. Circuit breaker

If a metric exceeds a limit:

\[
FailureRate>\tau
\]

or:

\[
Cost>Budget
\]

then:

\[
AgentExecution\rightarrow Stop
\]

This prevents cascades.

---

# 71. Runtime policy enforcement

2026 reinforces an important shift:

policy should not exist only in the prompt.

Architecture:

```text
LLM proposal
    ↓
policy middleware
    ↓
authz / risk check
    ↓
tool execution
    ↓
postcondition check
```

This is aligned with the direction of the OWASP Agent Control Standard.

---

# 72. Security evaluation

A secure system needs tests such as:

- direct prompt injection;
- indirect injection;
- poisoned retrieval;
- privilege escalation;
- tool misuse;
- memory poisoning;
- data exfiltration;
- resource exhaustion;
- malformed structured output;
- replay/retry edge cases.

See [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

# 73. Red-team versus benchmark

Benchmark:

\[
fixed\ distribution
\]

Red-team:

\[
adaptive\ adversary
\]

The attacker learns from the system's failures.

Both are necessary.

---

# 74. Attack success rate

\[
ASR=
\frac{successful\ attacks}{attempts}
\]

Always report it together with:

- attack class;
- threat model;
- permissions;
- number of retries;
- model/system version.

ASR without context is weakly comparable.

---

# 75. Robustness curve

Instead of one point, vary perturbation strength:

\[
Q(\epsilon)
\]

where:

\[
\epsilon=attack\ strength / noise / shift
\]

The area or slope of the curve is more informative than an arbitrary threshold.

---

# 76. Risk model

A useful approximation is:

\[
Risk
=Likelihood\times Impact
\]

For agents, expand impact as:

\[
Impact
=f(
Privilege,
Reach,
Irreversibility,
Sensitivity
)
\]

This helps determine where HITL or deterministic checks are required.

---

# 77. Failure taxonomy by layer

| Layer | Typical failure |
|---|---|
| `DATA` | poisoning, contamination |
| `MODEL` | backdoor, memorization, hallucination |
| `CONTEXT` | prompt injection, context poisoning |
| `RETRIEVAL` | poisoned corpus, auth leakage |
| `INFERENCE` | resource abuse, pathological settings |
| `TOOL` | misuse, privilege escalation |
| `AGENT` | goal hijack, cascading failure |
| `RUNTIME` | unsafe code/dependency/parser |
| `HUMAN` | automation bias, approval exploitation |

---

# 78. Control matrix

| Risk | Prevent | Detect | Contain/Recover |
|---|---|---|---|
| prompt injection | isolate content/capabilities | injection telemetry | deny action / reset context |
| RAG poison | signed/curated sources | provenance anomaly | remove doc/rebuild index |
| tool misuse | narrow APIs/authz | action logs | rollback/revoke token |
| memory poison | write policy | memory audit | delete/quarantine memory |
| supply chain | pin/hash/review | integrity monitoring | isolate/rebuild env |
| unbounded use | quotas | budget telemetry | circuit breaker |
| bad output | schema + semantic checks | validation failures | reject/retry/escalate |

---

# 79. NIST framing

The NIST AI RMF GenAI Profile treats risk across the lifecycle, not only at prompt time.

That matches this collection:

\[
Data
\rightarrow Training
\rightarrow Evaluation
\rightarrow Deployment
\rightarrow Monitoring
\]

Security and robustness must span all of them.

---

# 80. OWASP snapshot — 2026

In August 2026, OWASP published the **GenAI LLM Top 10 2026**, updated using real incidents and mappings to NIST/MITRE/CWE and the Agentic Top 10.

In September 2026, it published the **Agent Control Standard**, emphasizing runtime control and instrumentation.

This confirms a structural shift:

> AI security is no longer just “filter the prompts”; it is **control engineering for a system with agency, memory, tools, and a supply chain**.

---

# 81. Agentic Top 10 — useful classes for our map

The OWASP taxonomy for agentic systems includes:

1. Agent Goal Hijack;
2. Tool Misuse;
3. Identity & Privilege Abuse;
4. Agentic Supply Chain Vulnerabilities;
5. Unexpected Code Execution;
6. Memory & Context Poisoning;
7. Insecure Inter-Agent Communication;
8. Cascading Failures;
9. Human-Agent Trust Exploitation;
10. Rogue Agents.

These categories map directly to [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

---

# 82. Security is not prompt engineering

A rule worth preserving:

\[
SecurityControl
\not\subseteq
SystemPrompt
\]

A prompt can influence behavior.

A security boundary must exist in:

- identity;
- authorization;
- sandboxing;
- policy middleware;
- validation;
- transactions;
- network controls;
- filesystem controls;
- audit.

---

# 83. Incident response for AI systems

Minimum plan:

1. identify the trace/session/artifact;
2. block/revoke credentials;
3. contain tool/network access;
4. preserve logs/forensics;
5. determine the input/context/memory source;
6. identify model/runtime/plugin versions;
7. fix the control plane;
8. clean contaminated memories/indexes;
9. rerun adversarial regression tests;
10. update the threat model.

“Improve the prompt” is not an incident-response plan.

---

# 84. Security regression suite

Maintain versioned cases:

```text
PI-direct
PI-indirect
RAG-poison
memory-poison
unauthorized-read
unauthorized-write
credential-exfil
shell-injection
retry-double-action
budget-exhaustion
malformed-json
multimodal-injection
```

Every model/scaffold/runtime change reruns the suite.

---

# 85. Local-lab hardening checklist

1. Checksum important models.
2. Prefer `safetensors` where the ecosystem supports it.
3. Avoid unknown pickle artifacts.
4. Review `trust_remote_code`.
5. Run custom nodes in an isolated environment.
6. Pin dependencies.
7. Use explicit bind/authentication for local APIs.
8. Prevent accidental WAN exposure.
9. Keep secrets out of model context.
10. Give tools least privilege.
11. Redact logs.
12. Back up before giving agents write access.
13. Put destructive actions behind approval/transactions.
14. Control egress where practical.
15. Keep an action audit trail.

---

# 86. The final equation

\[
\boxed{
SecureAI
\neq
SafeModel
}
\]

More precisely:

\[
SecureSystem
=
f(
Model,
Data,
Context,
Identity,
Authorization,
Tools,
Runtime,
Observability,
Recovery
)
\]

The model is only one component of the threat surface.

---

# Checklist for dissecting risk in any system

1. What is the asset?
2. Who is a plausible attacker?
3. Which inputs are untrusted?
4. Which external sources enter context?
5. Is there persistent memory?
6. Is there retrieval?
7. Does retrieval enforce authorization before returning content?
8. Are there tools?
9. What permissions do they have?
10. Is the tool narrow or open-ended?
11. Is there shell/code execution?
12. Is there HITL for irreversible actions?
13. Does the approval UI show the real effect?
14. Is policy enforced outside the prompt?
15. Is there a sandbox?
16. Is network egress controlled?
17. Do secrets enter model context?
18. Can logs leak data?
19. Does the model/artifact have provenance and a hash?
20. Is there remote code or custom nodes?
21. Are dependencies pinned?
22. Are there rate/cost/token limits?
23. Are retries bounded and idempotent?
24. Is rollback available?
25. Is there a security regression suite?
26. Is there adversarial evaluation?
27. Is there an incident-response plan?
28. Does compromise of one component compromise the entire host?
29. Is there a blast-radius boundary?
30. Is the model treated as an untrusted component?

---

# Snapshot references

- OWASP GenAI LLM Top 10 2026 — https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
- OWASP Top 10 for Agentic Applications — https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/
- OWASP Agent Control Standard — https://genai.owasp.org/resource/agent-control-standard-acs/
- OWASP GenAI Top 10 initiative — https://genai.owasp.org/initiatives/top-10-for-llm-and-genai/
- NIST AI RMF Generative AI Profile — https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- NIST AI RMF — https://www.nist.gov/itl/ai-risk-management-framework
- Hugging Face Safetensors — https://huggingface.co/docs/safetensors/
