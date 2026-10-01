<div align="center">

# have-you-tried-reading-the-paper

### Uma explicação desnecessariamente detalhada sobre o que aquele botão realmente faz.

**Sem mágica. Só tensores, equações e papers que você provavelmente já deveria ter lido.**

[**English**](README.md) · [**Português (Brasil)**](README.pt-BR.md)

![Conhecimento Aberto](https://img.shields.io/badge/conhecimento%20aberto-feito%20para%20ser%20compartilhado-2ea44f)
[![Licença: CC BY-SA 4.0](https://img.shields.io/badge/licen%C3%A7a-CC%20BY--SA%204.0-1769aa)](LICENSE)
![Idiomas](https://img.shields.io/badge/idiomas-English%20%7C%20Portugu%C3%AAs-0969da)
![Base de Conhecimento](https://img.shields.io/badge/base%20de%20conhecimento-22%20docs%20por%20idioma-8250df)
![Escopo](https://img.shields.io/badge/escopo-engenharia%20de%20foundation%20models-f97316)
![Status](https://img.shields.io/badge/status-refer%C3%AAncia%20viva-1f883d)

</div>

---

> **Se uma interface te entrega um slider chamado _temperature_, _guidance_, _context_, _rank_, _steps_ ou _strength_, talvez seja uma boa ideia saber em qual equação você está mexendo antes de copiar a “melhor configuração” de outra pessoa.**

Interfaces de IA são propositalmente muito boas em esconder a máquina.

Isso é ótimo quando você só quer que o modelo faça alguma coisa.

É consideravelmente menos útil quando você quer entender **por que ele fez aquilo**, como manipular o resultado de forma sistemática, quais são os trade-offs reais, o que está acontecendo na memória ou por que alterar um parâmetro aparentemente inocente acabou de implodir qualidade, latência, VRAM, coerência temporal, recall do retrieval — ou os cinco ao mesmo tempo.

Este repositório é a camada **embaixo dos botões**.

É uma base aberta de conhecimento técnico para entender foundation models modernos de dentro para fora: representações, tensores, objectives, arquiteturas, estado, sampling, métodos numéricos, memória, treinamento, avaliação, segurança, agentes, retrieval, multimodalidade e a física de runtime que eventualmente transforma toda essa matemática elegante em calor.

Sem oráculo. Sem prompt mágico. Sem “segredos da IA”.

Só modelos.

---

## Por que isso existe

Existe uma quantidade absurda de material excelente sobre IA.

Existe também uma quantidade igualmente absurda desse material espalhada entre papers, código-fonte, documentação de frameworks, notas de implementação, benchmarks, issues, model cards e discussões escritas por gente que — perfeitamente razoável — assume que você já sabe o significado das trinta siglas anteriores.

Muitas vezes, o difícil não é encontrar **uma** explicação.

É construir o **modelo mental conectado** que mostra como as peças se relacionam.

Este projeto tenta tornar esse modelo explícito.

Em vez de:

```text
parâmetro -> sensação -> tenta outro valor
```

o alvo é:

```text
arquitetura
    -> estado
        -> equação
            -> controle
                -> perturbação
                    -> observável
                        -> output
                            -> custo físico
```

A proposta não é fingir que sistemas probabilísticos são determinísticos. Eles não são.

A proposta é deixar **mecanismos, variáveis controláveis, estados ocultos, dependências e superfícies de falha legíveis o suficiente para que seja possível fazer engenharia em cima deles**.

---

## O que você vai encontrar aqui

O material percorre o ciclo completo dos modelos em vez de usar “IA” como sinônimo de chatbot.

| Camada | O que cobre |
|---|---|
| **Teoria unificada** | Representações, objetivos generativos, backbones, conditioning, operadores de inferência, estado, decoding e topologia multimodal |
| **Famílias de modelos** | LLMs, código, imagem, vídeo, áudio/voz, 3D, multimodal/omni, séries temporais/tabular e graph foundation models |
| **Componentes de sistema** | Agentes, retrieval/reranking, reward models, verifiers, judges, world models e VLA/embodied AI |
| **Lifecycle** | Pretraining, post-training, alignment, PEFT, distillation, model merging, avaliação, benchmarking e experimentação |
| **Execução** | Quantização, KV cache, VRAM/RAM, offload, bandwidth, batching, prefill/decode e economia da inferência local |
| **Fronteiras de confiança** | Robustez, prompt injection, poisoning, supply chain, permissões de agentes, controles de runtime e failure modes |
| **Governança de conhecimento** | Convenções, terminologia canônica, registry de parâmetros, colisões semânticas e changelog |

E sim, tem equação.

Bastante.

---

## Comece por aqui

Para o mapa completo, abra o índice do idioma que você prefere:

### English
**[Open the English knowledge index →](docs/en-US/00_README_INDEX.md)**

### Português (Brasil)
**[Abrir o índice técnico em português →](docs/pt-BR/00_README_INDEX.md)**

Se você prefere ignorar a ordem sugerida e entrar diretamente num rabbit hole específico — decisão perfeitamente defensável — seguem alguns atalhos:

| Você quer entender... | Leia |
|---|---|
| o esqueleto matemático comum por trás da IA moderna | [`01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`](docs/pt-BR/01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| o que um LLM realmente faz entre o prompt e o próximo token | [`02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`](docs/pt-BR/02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| code completion vs. agentic coding | [`03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md`](docs/pt-BR/03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md) |
| diffusion, flow matching, DiTs, CFG, schedulers e solvers | [`04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md`](docs/pt-BR/04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md) |
| por que geração de vídeo faz sua GPU repensar as escolhas de vida | [`05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md`](docs/pt-BR/05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md) |
| geração de áudio, TTS, ASR e modelos de voz | [`06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`](docs/pt-BR/06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) |
| representações 3D geradas por IA | [`07_3D_GENERATION_REPRESENTATION_DATASHEET.md`](docs/pt-BR/07_3D_GENERATION_REPRESENTATION_DATASHEET.md) |
| tool calling, agentes e controle de ações | [`08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md`](docs/pt-BR/08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
| por que um modelo de 9 GB não necessariamente precisa só de 9 GB | [`09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`](docs/pt-BR/09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| VLMs, fusão multimodal e omni models | [`10_MULTIMODAL_VLM_OMNI_DATASHEET.md`](docs/pt-BR/10_MULTIMODAL_VLM_OMNI_DATASHEET.md) |
| embeddings, busca vetorial, retrieval em RAG e rerankers | [`11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md`](docs/pt-BR/11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md) |
| reward models, verifiers e LLM-as-a-judge | [`12_REWARD_VERIFIER_JUDGE_DATASHEET.md`](docs/pt-BR/12_REWARD_VERIFIER_JUDGE_DATASHEET.md) |
| world models, VLA e embodied AI | [`13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md`](docs/pt-BR/13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md) |
| foundation models para séries temporais e dados tabulares | [`14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md`](docs/pt-BR/14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md) |
| graph foundation models | [`15_GRAPH_FOUNDATION_MODELS_DATASHEET.md`](docs/pt-BR/15_GRAPH_FOUNDATION_MODELS_DATASHEET.md) |
| como modelos viram os pesos que você eventualmente baixa | [`16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`](docs/pt-BR/16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) |
| como fazer benchmark sem acabar medindo as próprias suposições | [`17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md`](docs/pt-BR/17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) |
| segurança, robustez e superfícies de falha | [`18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md`](docs/pt-BR/18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) |
| o que o nome de um parâmetro realmente significa naquele contexto | [`19_PARAMETER_GLOSSARY_AND_REGISTRY.md`](docs/pt-BR/19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |

---

## Estrutura do repositório

```text
.
├── README.md / README.pt-BR.md
├── LICENSE / CITATION.cff / .zenodo.json
├── PROVENANCE.md / PROVENANCE.pt-BR.md
├── CONTRIBUTING.md / CONTRIBUTING.pt-BR.md
├── CODE_OF_CONDUCT.md / SECURITY.md
├── docs/
│   ├── en-US/              # 00–19, CONVENTIONS.md, CHANGELOG.md
│   └── pt-BR/              # 00–19, CONVENTIONS.md, CHANGELOG.md
├── scripts/                # Validação local e testes de regressão
└── .github/                # CI, formulários de contribuição, CODEOWNERS
```

As duas árvores de idioma devem permanecer estruturalmente equivalentes.

A versão em inglês é o default do repositório. A edição em português brasileiro é mantida como versão de primeira classe — não como aquele parágrafo escondido perto do fim do README dizendo “also available in Portuguese”, seguido por uma tradução automática que parece documentação de impressora de 2004.

---

## As regras editoriais

Este repositório tem algumas opiniões.

### 1. Arquitetura não é comportamento

A família do modelo, seus pesos, procedimento de treinamento, algoritmo de inferência, runtime e interface que expõe tudo isso são **camadas diferentes**.

Dois controles terem o mesmo nome não significa que operem pelo mesmo mecanismo.

---

### 2. Uma analogia útil não é uma equação

Metáforas são bem-vindas. Falsas equivalências, não.

Se dois controles produzem um comportamento que _parece_ semelhante, mas atuam sobre objetos matemáticos diferentes, a distinção importa.

---

### 3. “Melhor configuração” quase sempre está sem metade da frase

Melhor para:

- qual modelo?
- qual backend?
- qual quantização?
- qual tamanho de contexto?
- qual objetivo?
- qual dataset?
- qual métrica?
- qual hardware?
- qual failure mode estamos aceitando?

Um preset é um **ponto de operação**, não uma lei da natureza.

---

### 4. Tamanho do modelo não é explicação suficiente

Contagem de parâmetros diz surpreendentemente pouco depois que MoE, quantização, KV cache, comprimento de contexto, tokens multimodais, sparsity, offload, bandwidth de memória e parâmetros ativos entram na sala.

No fim, o hardware manda a fatura.

---

### 5. Fonte primária ganha de folclore

Papers, especificações, código-fonte, documentação oficial, model cards e experimentos reproduzíveis têm prioridade sobre “um cara no Discord falou que 0.7 fica melhor”.

O cara do Discord pode estar certo.

Ele só não recebe imunidade diplomática contra evidência.

---

## Conhecimento, não misticismo

Este projeto evita deliberadamente apresentar sistemas de IA como caixas-pretas místicas.

Eles são máquinas estatísticas extraordinariamente complexas.

Isso já é interessante o suficiente.

Não precisamos inventar um fantasma dentro da multiplicação de matrizes.

Entender a máquina **não** torna esses sistemas determinísticos, perfeitamente interpretáveis ou totalmente previsíveis. Entrega algo muito mais útil:

**hipóteses melhores.**

E hipóteses melhores levam a experimentos melhores.

---

## Para quem é

Você provavelmente vai gostar deste repositório se:

- usa modelos locais ou frontier e quer entender o que existe embaixo do frontend;
- ajusta parâmetros de inferência e gostaria de parar de fazer isso exclusivamente por folclore;
- trabalha com ML, dados, software, infraestrutura, segurança, robótica, retrieval ou mídia generativa;
- aprende melhor com equações, diagramas de sistema, trade-offs e relações causais;
- está perfeitamente disposto a ler o paper, mas gostaria de saber **qual paper e por quê** antes.

Você **não** precisa de pós-graduação em Machine Learning.

Precisa de alguma tolerância a matemática e uma leve desconfiança de explicações mágicas.

---

## Como usar este repositório

Três estratégias razoáveis:

**Leia como um livro.**  
Comece pelo [índice em português](docs/pt-BR/00_README_INDEX.md) e siga a progressão sugerida.

**Use como manual de referência.**  
Vá direto à família de modelos, mecanismo ou parâmetro de que precisa.

**Use como companheiro de bancada.**  
Deixe o datasheet relevante aberto ao lado do llama.cpp, KoboldCpp, LM Studio, Ollama, SillyTavern, ComfyUI, stack de treinamento, benchmark harness ou qualquer frontend novo que tenha inventado outro nome para um parâmetro que já tinha nome.

---

## Uma referência viva

Documentação de IA tem uma propriedade inconveniente: começa a envelhecer aproximadamente cinco minutos depois de ser publicada.

Por isso, sempre que possível, o repositório separa:

- mecanismos matemáticos relativamente estáveis;
- comportamento dependente de arquitetura;
- detalhes de implementação de backend;
- heurísticas empíricas;
- snapshots tecnológicos datados.

A ideia é atualizar a camada que mudou em vez de reescrever todo o modelo mental sempre que um checkpoint novo fica famoso por quarenta e oito horas.

Consulte o [`CHANGELOG.md`](docs/pt-BR/CHANGELOG.md) e o [`CONVENTIONS.md`](docs/pt-BR/CONVENTIONS.md) para entender como a base evolui.

---

## Contribuindo

Correções, referências melhores, contraexemplos reproduzíveis, derivações mais claras, notas de implementação e adições genuinamente úteis são bem-vindas.

Antes de propor um datasheet completamente novo porque apareceu um modelo com nome brilhante, consulte primeiro as convenções do projeto:

**[Leia `CONVENTIONS.md` →](docs/pt-BR/CONVENTIONS.md)**

Nome novo de produto não constitui automaticamente uma nova categoria matemática.

Os departamentos de marketing já têm repositórios suficientes.

Ao contribuir com um idioma, manter o documento equivalente no outro idioma sincronizado é fortemente recomendado.

**[Guia de contribuição →](CONTRIBUTING.pt-BR.md)** · [Código de conduta](CODE_OF_CONDUCT.md) · [Política de segurança](SECURITY.md)

---

## Idiomas

- **English — default:** [`docs/en-US/`](docs/en-US/)
- **Português (Brasil):** [`docs/pt-BR/`](docs/pt-BR/)
- **Default README:** [`README.md`](README.md)

As duas edições buscam **equivalência conceitual**, não tradução constrangedora frase por frase.

Texto técnico merece coisa melhor.

---

## Licença

Salvo indicação em contrário, o conteúdo original deste repositório é licenciado sob **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

Você pode compartilhar, adaptar, traduzir, remixar e reutilizar o material — inclusive comercialmente — desde que dê a atribuição adequada, indique alterações quando aplicável e distribua adaptações sob a mesma licença.

**Copyright © 2026 Felipe Freitas Braga.**

Citações de terceiros, papers referenciados, marcas, materiais linkados, figuras, screenshots e outros elementos externos permanecem sujeitos aos direitos e licenças de seus respectivos titulares.

**[Leia a licença completa →](LICENSE)**

---

## Citação

Se este repositório contribuir materialmente para um trabalho acadêmico, científico, educacional ou técnico, por favor cite-o.

O repositório inclui um [`CITATION.cff`](CITATION.cff) legível por máquina, que o GitHub pode expor pelo recurso **Cite this repository** e converter para formatos padronizados de referência. Uma citação arquivada com DOI está planejada para uma release futura via Zenodo.

**[Metadados de citação →](CITATION.cff)**

---

## Produção assistida por IA e proveniência

Este projeto é **dirigido por humano e assistido por IA**.

Os datasheets originais do fim de 2025 foram predominantemente escritos por Felipe Freitas Braga e posteriormente revisados e refinados com assistência de IA. A reconstrução e expansão SOTA++ de 2026 utilizou extensivamente o OpenAI ChatGPT para síntese de pesquisa, redação técnica, reestruturação, revisão, localização para o inglês e controle de qualidade, enquanto arquitetura do projeto, padrões, escopo, julgamento técnico, decisões editoriais finais e responsabilidade pela publicação permaneceram sob controle humano.

A contribuição da IA é declarada intencionalmente em vez de escondida silenciosamente no histórico de commits. Ela foi material para a produção da base atual, mas o sistema de IA não aparece como autor acadêmico porque não pode assumir as responsabilidades e accountability próprias da autoria.

**[Leia a declaração completa de proveniência →](PROVENANCE.pt-BR.md)**

---

## Conhecimento aberto

Este projeto existe para tornar conhecimento técnico difícil mais fácil de acessar, conectar, inspecionar, questionar e redistribuir.

Conhecimento se multiplica quando as pessoas conseguem realmente chegar até ele.

Se alguma coisa aqui ajudar você a entender a máquina o suficiente para explicá-la melhor, testá-la com mais rigor, corrigi-la ou construir algo útil em cima dela, então o repositório está fazendo o trabalho dele.

---

<div align="center">

### Have you tried reading the paper?

**No magic. Just tensors.**

</div>
