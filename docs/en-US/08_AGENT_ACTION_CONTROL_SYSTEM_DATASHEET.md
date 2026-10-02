---
title: Agent & Action Control System Datasheet v2.0
tags: [ai, agents, tools, function-calling, mcp, control-systems]
updated: 2026-10-01
---

# Agent & Action Control System Datasheet v2.0

> An agent is not an “LLM that calls functions.” It is a **closed-loop control system** in which a model selects actions, an environment changes state, and new observations feed back into the policy.

## 1. Fundamental loop

```math
o_t=Observe(s_t)
```

```math
a_t\sim\pi_\theta(a\mid h_t,o_t,C)
```

```math
s_{t+1}=Environment(s_t,a_t)
```

```math
h_{t+1}=Update(h_t,o_t,a_t,result_t)
```

This is a feedback-driven dynamical system.

---

# PART I — ACTIONS

## 2. Action space

```math
\mathcal A=\{text,tool_1,tool_2,computer\_action,stop,\ldots\}
```

Each tool has a schema:

```math
a=(tool\_name,args)
```

### There is no universal “invocation threshold”

Some applications may include a classifier/confidence threshold, but in many systems tool selection is directly a policy/model decision.

Classify such a threshold as `PIPE/UI`, never as a universal `ARCH` property.

---

## 3. Tool choice

Possible regimes:

- `auto`;
- force a specific tool;
- “must use a tool”;
- text-only;
- external policy.

This restricts the action space:

```math
\mathcal A'\subseteq\mathcal A
```

---

# PART II — STRUCTURED OUTPUT

## 4. Schema-constrained decoding

Set of valid strings:

```math
L(Schema)
```

During decoding:

```math
p(x_t)=0\quad\forall x_t\notin ValidPrefix(Schema)
```

Depending on the implementation, this can strongly guarantee syntactic/structural validity.

### But:

```math
SchemaValid\neq SemanticallyValid
```

Example: `{"amount": 1000000}` may be perfect JSON under the schema and still represent an absurd or unauthorized action.

---

## 5. Four levels of validity

1. **Syntax** — does it parse?
2. **Schema** — are fields/types valid?
3. **Semantic** — do the arguments make sense?
4. **Authorization/Safety** — should the action be executed?

```math
V=V_{syntax}\land V_{schema}\land V_{semantic}\land V_{auth}
```

---

# PART III — STATE

## 6. History is not merely “N turns”

Useful state may include:

```math
h_t=\{conversation,tool\ results,files,IDs,plans,environment\ state,memory\}
```

History should be treated as a **state representation**, not simply a fixed number of messages.

---

## 7. State compression

Long-running agents need to compress:

```math
H_{raw}\rightarrow H_{compact}
```

Risk:

```math
Compression\uparrow\Rightarrow ContextCost\downarrow\ but\ InformationLoss\uparrow
```

Preserving IDs, handles, invariants, and decisions is generally safer than summarizing everything into prose.

---

# PART IV — PLANNING

## 8. Plan vs policy

Explicit plan:

```math
P=(a_1,a_2,\ldots,a_n)
```

Reactive policy:

```math
a_t=\pi(s_t)
```

Robust agents often combine a plan with replanning after observation.

### Important

Forcing visible chain-of-thought is not a universal requirement for better planning. What matters is the system's ability to decompose, verify, and correct actions.

---

## 9. Horizon

As the number of steps grows:

```math
P(success_{all})\approx\prod_tP(success_t\mid history)
```

Even 99% success per step:

```math
0.99^{100}\approx0.366
```

Long trajectories amplify small error rates.

### Engineering implication

Reducing the number of actions and increasing verifiability per action may be more valuable than simply using a “smarter model.”

---

# PART V — RETRIES

## 10. Retry policy

Retries should not be just `max_retries=3`.

Define:

- retryable errors;
- backoff;
- idempotency;
- max attempts;
- mutation detection;
- alternative strategy.

### Danger

Repeating a non-idempotent action:

```math
E(E(s,a),a)\neq E(s,a)
```

may duplicate payments, messages, uploads, and so on.

---

## 11. Idempotency

Ideal case:

```math
E(E(s,a),a)=E(s,a)
```

When that is impossible, use an idempotency key/transaction ID and inspect state before retrying.

---

# PART VI — TRANSACTIONS AND ROLLBACK

## 12. Prepare → validate → commit

For critical actions:

```math
Plan\rightarrow DryRun\rightarrow Validate\rightarrow Approve\rightarrow Commit
```

Separate action generation from execution.

### Rollback

If the operation has an inverse:

```math
a^{-1}(a(s))\approx s
```

record it as part of the plan.

Not every action is reversible.

---

# PART VII — HUMAN IN THE LOOP

## 13. HITL should be risk-based

Not simply one global `True/False` toggle.

Define:

```math
Risk(a)=Impact(a)\times Probability(error)\times Irreversibility(a)
```

Require approval when:

```math
Risk(a)>\tau
```

or based on capability class.

### Examples of high-risk actions

- send externally;
- delete;
- spend money;
- change permissions;
- publish;
- execute privileged code.

---

# PART VIII — CAPABILITIES

## 14. Least privilege

A policy should not receive tools it does not need.

```math
Capabilities_{agent}\subseteq Capabilities_{required}
```

The larger $`|\mathcal A|`$, the larger the decision space and attack surface.

---

## 15. Sandbox

Separate:

- read;
- write;
- execute;
- network;
- secrets;
- destructive operations.

A tool description is not a security mechanism. Enforcement must exist outside the LLM.

---

# PART IX — PROMPT/TOOL INJECTION

## 16. Data can contain instructions

Web pages, emails, documents, and tool results are potentially adversarial inputs.

Principle:

```math
UntrustedData\not\Rightarrow Authority
```

The agent must preserve instruction/capability hierarchy outside retrieved content.

---

# PART X — COMPUTER USE

## 17. GUI action loop

Visual observation:

```math
o_t=Vision(screen_t)
```

Action:

```math
a_t=(mouse/keyboard/navigation)
```

New state:

```math
screen_{t+1}=App(screen_t,a_t)
```

### Sources of error

- localization;
- stale screen;
- animation;
- focus;
- hidden state;
- ambiguous controls.

Computer use has lower observability than a structured API. Prefer APIs/tools when available.

---

# PART XI — VOICE-TO-ACTION

## 18. Correct pipeline

```math
audio\rightarrow VAD\rightarrow ASR\rightarrow agent/policy\rightarrow tool\rightarrow environment
```

Total latency:

```math
T=T_{VAD}+T_{ASR}+T_{LLM}+T_{tool}+T_{feedback}
```

VAD is an input subsystem, not a “LAM” parameter.

---

# PART XII — MCP

## 19. MCP as protocol, not intelligence

MCP standardizes connections between hosts and data/tool systems. It does not make the model semantically more reliable.

In the **2026-07-28** spec, the core protocol became stateless, added Multi Round-Trip Requests, header-based routing, list-result caching, an extensions framework, and Tasks as an extension.

### Architectural implication

Separate:

```math
Agent\ policy
```

from

```math
Tool\ transport/protocol
```

MCP addresses interoperability and lifecycle/protocol concerns; decision-making and security still belong to the agentic system.

---

# PART XIII — OBSERVABILITY

## 20. Essential metrics

- tool selection accuracy;
- schema-valid rate;
- semantic-valid rate;
- success/task completion;
- retries/action;
- steps/task;
- tokens/task;
- irreversible actions;
- rollback rate;
- permission denials;
- wall time;
- cost.

### Do not confuse

```math
ToolCallRate\neq TaskSuccess
```

An “active” agent may simply be failing a lot.

---

# PART XIV — COUPLING MATRIX

| Control ↑ | Autonomy | Potential success | Risk | Cost |
|---|---:|---:|---:|---:|
| tool set size | ↑ | may ↑ | ↑ | ↑ decision complexity |
| max steps | ↑ | ↑ until plateau | ↑ | ↑ |
| retries | ↑ | ↑ under transient failure | ↑ duplication | ↑ |
| HITL | ↓ autonomy | ↑ safety | ↓ | ↑ human latency |
| schema strictness | ↓ malformed calls | ~ semantic | ↓ syntax risk | small |
| state compression | ~ | may ↓ | lost information ↑ | ↓ context cost |

---

# PART XV — FAILURE DIAGNOSTICS

| Symptom | Layer |
|---|---|
| invalid JSON | constrained decoding/schema |
| fabricated argument | semantic policy/missing-data handling |
| calls wrong tool | tool selection/descriptions/context |
| repeats action | state/idempotency/retry |
| loses file/ID | state representation |
| dangerous action | capability/HITL/enforcement |
| browser enters loop | observability/stale UI/horizon |

---

## 21. Snapshot 2026

MCP 2026-07-28 is the most important snapshot of the current open agentic infrastructure: stateless core, explicit state handling, Multi Round-Trip Requests, formal extensions, and Tasks. It reinforces the shift in mental model: an “action model” is not an isolated checkpoint category; it is a **control system + protocol + environment + policy**.

## References

- MCP 2026-07-28 — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- MCP TypeScript SDK v2 — https://ts.sdk.modelcontextprotocol.io/v2/
