# Camadas de dados — Brasil

## Tier A — fonte oficial/primária

Priorizar conforme competência e disponibilidade: PNCP, Compras.gov.br, Portal da Transparência, TCU, CGU, TCE/TCM, MPs, TSE/TRE, CNJ/tribunais, SICONFI, diários oficiais, portais do ente, Receita/CNPJ em consulta ou dados abertos legítimos, juntas comerciais quando o acesso for público e adequado.

## Tier B — estruturado institucional/derivado

Pode acelerar descoberta e normalização, mas o claim sensível deve voltar ao documento/origem oficial quando possível.

## Tier C — enriquecimento investigativo

OpenSanctions, Aleph e ferramentas semelhantes podem gerar candidatos de entidade e conexões. O match não fecha identidade nem sanção brasileira sem validação na fonte original.

## Tier D — referência metodológica

Projetos como Serenata de Amor são valiosos para arquitetura de civic-tech e detecção de anomalias, mas não devem ser tratados como fonte atual de fatos de um caso.

## Fontes não públicas

SCR/Bacen, sigilo bancário, fiscal ou telefônico e bases restritas não fazem parte do runtime aberto. A VTB deve registrar `FORMAL_DILIGENCE_REQUIRED` quando uma hipótese depende desse tipo de prova.

## Nota sobre Minha Receita

O projeto `cuducos/minha-receita` é uma referência histórica útil para consulta de CNPJ, porém o repositório está arquivado. A VTB não o considera dependência estratégica primária e deve privilegiar dados oficiais ou adapters mantidos e testados.
