# Entity matching e PEP/sanctions

VTB não transforma um resultado de busca nominal em identidade confirmada.

## Yente/OpenSanctions

O adapter usa a API de matching por exemplo (`POST /match/{dataset}`), preserva os identificadores enviados, score retornado e dataset. A documentação/código upstream informa que a precisão depende do detalhamento da entidade: para pessoas, nome combinado com data de nascimento, nacionalidade/país, identificador e endereço aumenta capacidade de desambiguação.

Saída do adapter: **candidate match**.

Para claim sensível (PEP, sanção, pessoa de interesse):

1. resolver identidade;
2. verificar datas e país;
3. localizar a fonte/lista original quando disponível;
4. registrar a linhagem OpenSanctions → dataset → fonte original;
5. preservar contradições/falsos positivos;
6. somente então classificar o claim.

## CNPJ

A VTB possui adapter local para snapshot JSONL. O snapshot precisa de manifesto de origem, data, competência, hash e licença/termos. O projeto Minha Receita é referência de arquitetura, mas seu repositório GitHub foi movido/arquivado e não é dependência obrigatória do runtime.
