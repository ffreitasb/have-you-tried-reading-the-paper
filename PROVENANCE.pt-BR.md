# Proveniência do Projeto e Declaração de Assistência por IA

## Por que este arquivo existe

Este repositório documenta não apenas **o que** contém, mas também **como a base de conhecimento foi produzida**.

Isso importa por dois motivos:

1. trabalho técnico deve ser transparente sobre as ferramentas e processos que contribuíram materialmente para sua produção; e
2. um projeto dedicado a entender sistemas de IA por baixo do capô provavelmente não deveria fingir que IA não participou da sua própria construção.

A versão curta:

> **Este é um projeto técnico dirigido por humano e produzido com assistência de IA.**

Felipe Freitas Braga é o autor humano, editor, mantenedor e responsável pela publicação do repositório. O OpenAI ChatGPT foi utilizado de forma extensiva como assistente de pesquisa, síntese, redação, reestruturação, revisão, localização e controle de qualidade durante a reconstrução e expansão do material em 2026. A engenharia do repositório e a revisão científica posteriores utilizaram o OpenAI Codex, incluindo rodadas de revisão e correção com GPT-6 Astra, conforme descrito abaixo.

---

## Proveniência histórica

### Material original — fim de 2025

Os primeiros datasheets foram criados para estudo pessoal e armazenados em uma base privada no Obsidian.

Esses documentos originais foram **predominantemente escritos por Felipe Freitas Braga**, com IA utilizada principalmente para revisar, refinar, questionar e melhorar material que já havia sido estruturado e redigido pelo autor humano.

O objetivo original era pragmático: expor a matemática e a mecânica computacional escondidas pelas interfaces amigáveis de IA, especialmente os parâmetros e estados que determinam o comportamento dos modelos durante a inferência.

### Reconstrução e expansão SOTA++ — outubro de 2026

O repositório atual é uma reconstrução muito maior daquela base inicial.

Nesta fase, o fluxo de produção passou a ser substancialmente mais assistido por IA. O OpenAI ChatGPT contribuiu materialmente para:

- assistência de pesquisa e descoberta de fontes;
- síntese entre papers, especificações, código-fonte, documentação de modelos e notas de implementação;
- redação e reescrita técnica;
- exposição matemática e notação;
- comparação entre domínios e desenho da taxonomia;
- normalização estrutural dos datasheets;
- consistência terminológica;
- identificação de lacunas conceituais e premissas desatualizadas;
- localização da edição em português para o inglês;
- revisão editorial e controle de qualidade mecânico.

A contribuição humana permaneceu decisiva e não delegada em:

- definir propósito, escopo, filosofia e voz editorial do projeto;
- decidir o que merecia constituir uma categoria distinta de modelo ou sistema;
- definir a ontologia e arquitetura documental;
- estabelecer profundidade técnica e padrões de evidência;
- direcionar o processo de pesquisa e revisão;
- questionar, corrigir, aceitar, rejeitar e reestruturar material gerado pela IA;
- decidir a redação, organização, licenciamento e modelo de publicação finais;
- assumir responsabilidade pelo resultado publicado.

A expansão de 2026, portanto, não foi nem "escrita inteiramente por IA" nem "escrita inteiramente por um humano com um pouco de autocomplete". Foi um **fluxo colaborativo de produção em que o humano forneceu direção, julgamento, padrões, contexto de domínio e responsabilidade final, enquanto a IA forneceu uma parcela substancial do trabalho de pesquisa, síntese, redação e edição**.

Tentar resumir isso a uma porcentagem exata produziria uma precisão que o processo não comporta.

---

### Engenharia do repositório e renderização matemática — outubro de 2026

O OpenAI Codex auxiliou na organização do repositório, navegação portável, documentação de contribuição e governança, integração de citação e arquivamento, validação automatizada e investigação e correção de falhas de renderização matemática no GitHub e em builds temporários do MkDocs.

As correções de renderização alteraram delimitadores e grafias TeX equivalentes explicitamente revisadas. Suas verificações de preservação separaram mudanças de apresentação de mudanças no significado científico. A release arquivada v1.0.0 não foi reescrita.

### Revisão científica e correções bilíngues — 9 a 16 de outubro de 2026

A pedido do mantenedor, agentes GPT-6 Astra no Codex revisaram os 44 documentos das edições em inglês e português brasileiro. A revisão abrangeu afirmações técnicas, equações e seus domínios, dimensões de tensores, hipóteses, fontes e consistência conceitual dentro de cada edição e entre elas. O trabalho combinou consulta a fontes primárias com cálculos direcionados e contraexemplos reproduzíveis.

O mantenedor então autorizou as correções. O ciclo concluído tratou 47 achados consolidados no corpus e um no guia de contribuição, além de esclarecer 46 registros condicionais ou editoriais. Esses números descrevem os achados dessa revisão, não uma contagem exaustiva de todos os erros possíveis. Questões materiais de intenção foram encaminhadas ao mantenedor: o exemplo contrastivo preserva sua fórmula e é identificado como aprendizagem contrastiva desacoplada (DCL); a comparação corrompida entre templates foi substituída por prosa sobre compatibilidade de serialização, sem exigir entradas de treino e inferência idênticas byte a byte.

O Codex auxiliou na implementação das correções pareadas, revisão dos diffs, registro exato dos trechos antes/depois e execução dos checks de integridade e renderização. A verificação de 16 de outubro cobriu 22 testes de regressão e 3.025 expressões matemáticas no parser nativo, em builds temporários do MkDocs e no componente real de renderização do GitHub em fixtures descartáveis de navegador, com inspeção representativa em desktop/mobile. Uma fixture verifica a renderização candidata; ela não demonstra que as alterações foram publicadas ou que um site de documentação está em produção.

A avaliação científica e a verificação mecânica permanecem separadas. Hashes coincidentes, MathML válido e testes aprovados não provam a veracidade de uma afirmação técnica. O trabalho foi uma revisão assistida por IA sob direção humana, não uma revisão por pares humanos independentes nem uma reprodução de todos os benchmarks e treinamentos citados. O mantenedor conserva a responsabilidade editorial e de publicação; esses checks não implicam que ele tenha rederivado pessoalmente cada equação.

O [changelog da edição](docs/pt-BR/CHANGELOG.md) registra as correções conceituais. O [registro de revisões de conteúdo](scripts/content-revisions.json) documenta fingerprints revisados de antes/depois, identificadores de revisão e fontes, preservando a baseline histórica de formatação. Consulte a [manutenção da renderização matemática](scripts/MATH_RENDERING.md) para conhecer o alcance dessas verificações.

---

## Sistemas de IA utilizados

As ferramentas e configurações de modelo registradas têm papéis distintos na história do projeto:

- **OpenAI ChatGPT, GPT-5.6 Sol:** reconstrução, expansão e localização iniciais de outubro de 2026.
- **OpenAI Codex:** engenharia posterior do repositório, correções de renderização, implementação e verificação.
- **GPT-6 Astra no Codex:** rodadas de revisão e correção científica das duas edições em outubro de 2026.

Nomes de modelos, configurações e comportamento do produto podem mudar ao longo do tempo. Esses nomes identificam as etapas registradas de produção e revisão; não são dependências de runtime do repositório nem implicam que todas as tarefas utilizaram o mesmo modelo.

---

## Por que a IA não aparece como autora acadêmica

A utilização de IA é declarada de forma explícita, mas o sistema de IA **não aparece como autor no `CITATION.cff`**.

Autoria não é apenas uma medida de quantas palavras ou rascunhos um participante produziu. Em contextos acadêmicos e técnicos, autoria também implica responsabilidade, accountability, capacidade de aprovar a versão final, responder por erros, administrar conflitos de interesse e sustentar publicamente as afirmações feitas.

Um sistema de IA não consegue assumir essas obrigações de forma significativa.

Assim:

- a assistência de IA é declarada como **contribuição material de produção**;
- o mantenedor humano permanece como **autor e responsável pela publicação**;
- o repositório não esconde, minimiza ou representa incorretamente o papel da IA na sua criação.

---

## Política de fontes e evidência

Síntese assistida por IA não valida uma afirmação por si só.

Por isso, o projeto prioriza, sempre que viável:

1. papers de pesquisa primários;
2. especificações e padrões formais;
3. código-fonte e documentação de implementação;
4. model cards e relatórios técnicos oficiais;
5. experimentos reproduzíveis e metodologia de benchmark;
6. explicações secundárias apenas quando acrescentam contexto útil.

Ainda assim, leitores devem verificar afirmações importantes nas fontes primárias citadas, especialmente em áreas de evolução rápida nas quais detalhes de implementação e comportamento dos modelos mudam constantemente.

O repositório é um mapa técnico, não um oráculo.

---

## Proveniência da tradução e localização

A edição em inglês não é uma tradução literal automática da edição em português.

Ela foi produzida por **localização técnica assistida por IA**, preservando equações, estrutura, escopo e conteúdo conceitual, mas reescrevendo a prosa para soar natural a um público técnico nativo em inglês.

O objetivo é equivalência conceitual, não simetria lexical frase por frase.

---

## Escopo do licenciamento

Salvo indicação em contrário, o conteúdo original do repositório é disponibilizado sob a **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

A licença se aplica apenas aos direitos que o licenciante pode legalmente conceder. Citações de terceiros, papers referenciados, marcas, materiais linkados, screenshots, figuras ou outros elementos externos permanecem sujeitos aos direitos e licenças de seus respectivos titulares.

Consulte [`LICENSE`](LICENSE) para o texto integral da licença.

---

## Citação

Se este repositório contribuir materialmente para um trabalho acadêmico, científico, educacional ou técnico, utilize os metadados disponíveis em [`CITATION.cff`](CITATION.cff) para citá-lo.

O arquivamento no Zenodo e a citação via DOI estão implementados. A release imutável v1.0.0 está publicada no [arquivo do Zenodo](https://zenodo.org/records/23092486) com DOI [10.5281/zenodo.23092486](https://doi.org/10.5281/zenodo.23092486), que identifica essa versão exata. O [DOI do projeto](https://doi.org/10.5281/zenodo.23092485) representa todas as versões.

A release [v1.1.0](https://github.com/ffreitasb/have-you-tried-reading-the-paper/releases/tag/v1.1.0) consolida as correções posteriores de formatação e conteúdo científico descritas acima, sem acrescentar capítulos. Ela está arquivada no [registro 23427536 do Zenodo](https://zenodo.org/records/23427536), com DOI [10.5281/zenodo.23427536](https://doi.org/10.5281/zenodo.23427536). Ela não altera retroativamente a v1.0.0 nem seus metadados de citação. Cada release arquivada tem seu próprio DOI de versão; use o DOI da versão efetivamente consultada. Ao referenciar material de `main`, registre também o SHA do commit ou um permalink que identifique a revisão utilizada.

---

## Contato

Para assuntos relacionados ao projeto:

**Felipe Freitas Braga**  
`contact@ffreitasb.cc`

---

> Transparência custa menos do que fingir que a ferramenta não ajudou.
