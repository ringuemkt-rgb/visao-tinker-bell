# Pipeline Brasil — Visão Tinker Bell

## Fontes prioritárias e ordem de coleta

1. **TSE Dados Abertos**
   - consulta_cand_{ano}.zip
   - bem_candidato_{ano}.zip
   - prestações de contas (receitas e despesas)
   - Filiações partidárias

2. **Portal da Transparência / CGU**
   - Contratos
   - Emendas parlamentares
   - Transferências
   - CEIS / CNEP
   - Lista de Pessoas Expostas Politicamente (PEPs)

3. **Receita Federal — CNPJ**
   - Dumps mensais completos (QSA = quadro de sócios e administradores)

4. **Câmara e Senado**
   - Votações nominais
   - Gastos CEAP / CEAPS

5. **OpenSanctions Brazil + TCU**

## Passos operacionais

1. Download com registro de evidência (URL + data + SHA-256).
2. Normalização de CPF e CNPJ (remover pontuação, validar dígitos verificadores).
3. Entity resolution (matching por CPF/CNPJ + nome normalizado + fuzzy quando necessário).
4. Joins:
   - Bens TSE ↔ crescimento entre eleições
   - Doações ↔ CNPJ de empresas doadoras
   - Emendas/contratos ↔ CNPJ de favorecidos
   - QSA ↔ parentesco / sócios em comum
5. Construção do grafo (nós = pessoas/empresas, arestas = doacao | contrato | socio | familiar).
6. Scoring de consistência e anomalia.
7. ACH + visualização.
8. Dossiê final com apêndice de evidências.

## Scripts de apoio

- `scripts/tse_download.py` — ponto de partida para TSE
- Expandir com loaders específicos para cada fonte oficial
- Export GraphML/GEXF para Gephi e Neo4j

Nunca commitar dados brutos sensíveis no repositório. Use `.gitignore` e pastas `data/raw` locais.
