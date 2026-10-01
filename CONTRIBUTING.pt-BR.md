# Como contribuir

[English](CONTRIBUTING.md) · [Português (Brasil)](CONTRIBUTING.pt-BR.md)

Este projeto é uma referência técnica bilíngue sobre a máquina escondida pelas interfaces de IA. Correções, fontes melhores, contraexemplos reproduzíveis e notas úteis de implementação são bem-vindos. Um anúncio de produto precisa ter um mecanismo a explicar antes de precisar de um datasheet.

## Evidência e rigor técnico

Priorize papers primários, especificações formais, código-fonte e documentação oficial de implementação, model cards e relatórios técnicos, seguidos de experimentos reproduzíveis. Explicações secundárias podem ajudar a contextualizar; uma resposta gerada por IA não constitui evidência por si só.

Ao propor uma correção, indique documento e seção, cite a afirmação atual, apresente a substituição e aponte uma fonte confiável com seção, equação ou experimento reproduzível. Separe fatos matemáticos, premissas de arquitetura, comportamento de backend e recomendações empíricas. Não altere afirmações técnicas sem evidência. Preserve equações e terminologia, salvo quando forem o objeto da correção.

Leia as [convenções em português](docs/pt-BR/CONVENTIONS.md) ou as [convenções em inglês](docs/en-US/CONVENTIONS.md) para entender ontologia, estrutura dos datasheets, tags de proveniência e manutenção. Esses arquivos regem o conteúdo técnico; este guia orienta o processo de contribuição.

## Duas edições, mesmo escopo

Mantenha os mesmos nomes de arquivo e o mesmo escopo conceitual nas duas edições. Uma correção técnica deve atualizar ambos os idiomas. Se você não conseguir preparar a outra edição, declare isso na issue ou no pull request e indique qual documento precisa de localização; o mantenedor deve resolver essa lacuna antes de integrar uma mudança que afete afirmações técnicas compartilhadas. Prefira uma localização natural. Contagem de frases e tradução literal não medem paridade.

## Novas categorias e datasheets

Abra uma proposta estrutural antes de adicionar documentos numerados ou alterar a ontologia. Explique o que muda em representação, objetivo, topologia de inferência ou dinâmica de estado, por que os documentos existentes não atendem, quais fontes sustentam a proposta e qual o impacto nas duas edições e na navegação.

Nome novo de produto ou modelo não constitui automaticamente uma nova categoria matemática.

## Fluxo de trabalho

1. Use o [formulário de issue adequado](https://github.com/ffreitasb/have-you-tried-reading-the-paper/issues/new/choose) para correções, referências, localização ou propostas estruturais. Ajustes pequenos e bem fundamentados podem chegar diretamente por pull request.
2. Crie uma branch a partir de `main`, limite o escopo e preencha o template do pull request. Explique qualquer impacto nos metadados de citação ou release.
3. Execute as mesmas verificações determinísticas do CI com Python 3.12 ou mais recente:

   ```sh
   python -m venv .venv
   # Ative .venv com o comando habitual do seu shell.
   python -m pip install -r scripts/requirements-validation.txt
   python scripts/validate_repository.py
   python -m unittest discover -s scripts -p "test_*.py"
   cffconvert --validate -i CITATION.cff
   ```

O validador não modifica arquivos. Ele verifica estrutura, links locais e fragmentos determinísticos, higiene de texto, metadados de citação e o espelho do Zenodo quando presente. Referências externas passam por um workflow separado, semanal ou manual, com relatório para download; uma falha de rede não demonstra que uma afirmação técnica está errada.

Não inclua estado de editor, memória de agentes, credenciais ou saídas locais de build nos commits. Encaminhe problemas ativos de segurança em particular, conforme a [política de segurança](SECURITY.md). A participação na comunidade segue o [código de conduta](CODE_OF_CONDUCT.md).

## Assistência por IA, atribuição e licença

Declare no pull request a assistência material de IA: qual ferramenta ajudou em quais etapas e como você verificou o resultado. A responsabilidade por evidência, precisão, direitos e contribuição final é sua. Consulte a [declaração de proveniência](PROVENANCE.pt-BR.md). Sistemas de IA não aparecem como autores acadêmicos nos metadados de citação.

Ao enviar material original para inclusão, você concorda com sua distribuição sob [CC BY-SA 4.0](LICENSE). Identifique material de terceiros, sua fonte e licença; não envie conteúdo que você não tenha direito de contribuir. Preserve a atribuição adequada. Versões do repositório e metadados DOI são mantidos pelo responsável pela publicação; tags de releases publicadas permanecem imutáveis.
