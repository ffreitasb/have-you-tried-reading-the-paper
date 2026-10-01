---
title: Code Generation & Agentic Coding Datasheet v2.0
tags: [ai, code, fim, agents, software-engineering]
updated: 2026-10-01
---

# Code Generation & Agentic Coding Datasheet v2.0

> Code has two mathematically different phases: **generating plausible tokens** and **producing a valid state transition in a software system**. In 2026, SOTA coding is increasingly less “autocomplete” and more “closed-loop software engineering.”

## 1. Two machines

### A. Completion engine

\[
p(code_t\mid code_{<t},context)
\]

### B. Coding agent

\[
a_t\sim\pi(a\mid repo_t,conversation_t,tool_t,test_t)
\]

\[
repo_{t+1}=Environment(repo_t,a_t)
\]

Final quality depends on the entire loop, not just the probability of the next token.

---

# PART I — COMPLETION

## 2. Left-to-right completion

\[
P(x_{1:T})=\prod_tP(x_t\mid x_{<t})
\]

Suitable for:

- file generation;
- function continuation;
- boilerplate;
- technical chat.

---

## 3. Fill-In-the-Middle — FIM

Problem:

\[
P(M\mid Prefix,Suffix)
\]

Serializations vary by tokenizer/model, but conceptually there are three regions:

- prefix;
- suffix;
- middle.

### Why it works better than “prompting the hole”

The model is explicitly trained to use both left **and** right context. That is different from merely describing the suffix in natural language inside the prompt.

### Variables

| Variable | Tag | Effect |
|---|---|---|
| FIM tokens/template | `MODEL` | infilling protocol |
| prefix length | `INF` | preceding context |
| suffix length | `INF` | downstream constraints |
| max completion | `INF` | patch size |
| stop conditions | `INF` | terminates scope |

---

## 4. Sampling for code

There is no universal “temperature 0 always.” The objective defines the regime.

### Deterministic completion

- low temperature;
- restricted support;
- correct stop/FIM handling.

### Architecture/refactoring exploration

May justify higher entropy to propose alternatives.

### Rule

\[
Correctness\not\equiv low\ temperature
\]

A distribution concentrated on the wrong answer is still wrong.

---

## 5. Repetition penalties in code

Code contains legitimate repetition:

- indentation;
- delimiters;
- names;
- parallel structures;
- imports;
- boilerplate.

Aggressive penalties can degrade syntax or identifier consistency.

Use DRY/repetition penalties more conservatively than you would for creative prose.

---

# PART II — REPOSITORY CONTEXT

## 6. Repository context ≠ context window

Having 128k tokens available does not mean you should stuff the entire repository into context.

Selection problem:

\[
S^*=\arg\max_S Utility(S\mid task),\quad |S|\le budget
\]

Sources:

- target file;
- imports;
- symbols/references;
- interfaces/types;
- tests;
- build config;
- README/spec;
- recent diffs.

### Failure mode

Irrelevant context consumes tokens and may reduce signal-to-noise ratio.

---

## 7. Retrieval and symbol graph

Lexical search only finds similar text. Better coding agents combine:

- filename/path priors;
- symbol lookup;
- references/call graph;
- semantic search;
- AST/tree-sitter;
- compiler/LSP feedback.

Conceptual representation:

\[
Repo\rightarrow Graph(V_{symbols/files},E_{imports/calls/refs})
\]

Task context is a relevant subnetwork of that graph.

---

# PART III — EDITING

## 8. Full rewrite vs patch

### Full rewrite

\[
file' = LLM(file,instruction)
\]

Risk: large collateral changes.

### Patch/diff

\[
\Delta=LLM(context,instruction)
\]

\[
file'=apply(file,\Delta)
\]

More economical and auditable, but the patch must match the current file state.

---

## 9. Structured edit

Better still when the action is represented as an operation:

\[
a=(file,start,end,replacement)
\]

or an AST transformation.

This separates:

- generation of edit intent;
- deterministic application mechanism.

---

# PART IV — AGENT LOOP

## 10. The real loop

\[
Observe\rightarrow Select\ Context\rightarrow Plan/Policy\rightarrow Act\rightarrow Execute\rightarrow Observe
\]

State:

\[
s_t=(repo_t,terminal_t,test_t,conversation_t,tool_t)
\]

Action:

\[
a_t\in\{read,search,patch,run,test,git,\ldots\}
\]

Transition:

\[
s_{t+1}=E(s_t,a_t)
\]

---

## 11. Environment feedback

Compilers/tests are **partial oracles**.

\[
feedback=f(code')
\]

Examples:

- parser;
- type checker;
- compiler;
- unit tests;
- integration tests;
- linter;
- benchmark.

The agent can iterate:

\[
a_{t+1}=\pi(s_t,feedback_t)
\]

This is qualitatively different from one-shot code generation.

---

## 12. Verifiable rewards

Coding is especially suitable for RL/agentic training because many tasks expose verifiable signals:

\[
r\in\{test\ pass,compile,benchmark,judge\}
\]

Qwen3-Coder-Next is a 2026 example of agentic training with verifiable tasks and executable environments.

---

# PART V — CORRECTNESS

## 13. Correctness hierarchy

1. **Lexical validity**
2. **Syntax validity**
3. **Type/static validity**
4. **Runtime validity**
5. **Test validity**
6. **Spec/semantic validity**
7. **Security/non-functional validity**

Passing level \(n\) does not guarantee \(n+1\).

\[
SyntaxCorrect\not\Rightarrow SemanticallyCorrect
\]

---

## 14. Structured output for tools

Tool calls should use schema/constrained decoding whenever possible.

But:

\[
JSONValid\not\Rightarrow ToolCallCorrect
\]

So validation should happen in two phases:

1. schema validation;
2. semantic/precondition validation.

---

# PART VI — SECURITY

## 15. Agentic coding expands the attack surface

A bad autocomplete emits bad text. A bad coding agent can:

- delete files;
- run arbitrary shell commands;
- leak secrets;
- modify CI;
- publish artifacts;
- change dependencies.

### Recommended control

\[
permission(a_t)\le granted\ capability
\]

Principles:

- least privilege;
- sandbox;
- read-only by default;
- tool allowlist;
- approval for irreversible actions;
- secret isolation;
- diff review before commit/push.

---

## 16. Prompt injection in repository context

Files inside the repository itself may contain malicious or accidental instructions.

Keep separate:

\[
Data\neq Instruction
\]

A comment in a README should not automatically inherit system-prompt authority.

---

# PART VII — REPRODUCIBILITY

## 17. A fixed seed is not enough

\[
R=f(weights,tokenizer,template,repo\ state,tool\ outputs,sampler,seed,backend,hardware)
\]

With agents, the environment itself changes:

\[
Environment_t\neq Environment_{t+1}
\]

- package versions;
- network responses;
- timestamps;
- filesystem;
- concurrent processes.

Reproducing an agentic trajectory requires an environment snapshot, not just a seed.

---

# PART VIII — COST MODEL

## 18. Context economics

Approximate total cost:

\[
Cost=C_{prefill}(repo\ context)+\sum_t C_{decode}(t)+\sum_j C_{tools,j}
\]

Long-running agents may spend more context reprocessing history than generating code.

### Optimizations

- prompt caching;
- tool-result summarization;
- compact state;
- targeted retrieval;
- patch-oriented edits;
- truncation of irrelevant logs.

---

# PART IX — COUPLING MATRIX

| Control ↑ | Correctness | Diversity | Latency | Collateral risk |
|---|---:|---:|---:|---:|
| Temperature | variable/↓ in excess | ↑ | ~ | ↑ |
| Relevant context | ↑ | ~ | ↑ | ↓ |
| Irrelevant context | potentially ↓ | ~ | ↑ | ↑ |
| Test iterations | ↑ | ~ | ↑ | ↓ |
| Agent horizon | ↑ up to a point | — | ↑ | ↑ after loops |
| Tool permissions | — | — | — | ↑ dramatically |
| Smaller patch granularity | ↑ auditability | — | may ↑ steps | ↓ |

---

# PART X — PRACTICAL MAPPING

## 19. Autocomplete/FIM

Choose a model with genuine FIM support and the correct template. Verify special tokens in the tokenizer/model card.

## 20. Cline/Continue/agent harness

Evaluate separately:

- model quality;
- retrieval/context builder;
- tool interface;
- diff application;
- terminal loop;
- permissions.

Changing only the model does not measure the agentic system.

## 21. Local models

On constrained hardware, MoE can provide favorable active compute, but total storage still matters. An “80B total / 3B active” model does not magically fit in VRAM like a 3B model.

---

# PART XI — EXPERIMENTAL PROTOCOL

## 22. Useful benchmark

Use your own corpus with tasks such as:

1. complete a function;
2. FIM inside a real file;
3. fix a unit-tested bug;
4. perform a multi-file refactor;
5. add a feature with tests;
6. resolve a build error;
7. navigate a repository without being told which file matters.

Measure:

- compile rate;
- test pass rate;
- edit distance;
- files touched;
- tool calls;
- retries;
- tokens;
- wall time;
- regressions.

---

## 23. Snapshot 2026

Qwen3-Coder-Next illustrates the current direction: an 80B-total / ~3B-active-per-token MoE trained for coding agents through verifiable tasks and executable environments. The relevant axis is no longer merely “which model completes best?” but “which policy closes the engineering loop in fewer steps and with less collateral damage?”

## References

- Qwen3-Coder-Next — https://arxiv.org/abs/2603.00729
- llama.cpp FIM/samplers — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
