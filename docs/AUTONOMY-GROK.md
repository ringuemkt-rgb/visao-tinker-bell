# Integração Grok Bot + Visão Tinker Bell — autonomia controlada

## Entregue nesta branch
- Duas skills nativas do Grok Build em `.grok/skills/`: investigação brasileira e HUMAN WRITING OS.
- `vtb.autonomy`: plano de 1 a 5 consultas públicas, validação de parâmetros, operações allowlisted e executor somente-leitura com auditoria no CaseStore.
- Ferramentas MCP `plan_public_queries`, `run_public_queries`, `optional_toolcheck` e `draft_official_notice` (caso pré-cadastrado).
- Testes offline de restrição de operações, tratamento de falhas e registro de execução.

## Capacidades reais e limites
Não existe conexão automática apenas por subir código ao GitHub. A skill Grok Build é descoberta ao abrir o repositório nesse ambiente. O Grok Bot em nuvem precisa de um servidor MCP HTTPS acessível e autenticado. O MCP já existente usa Python, pacote opcional `mcp` e `streamable-http`, mas **não** disponibiliza por si só autenticação remota, isolamento multiusuário, gateway TLS, RBAC ou implantação em nuvem.

As tools disponíveis executam somente consultas específicas a PNCP, TSE e cadastros de sanções do Portal da Transparência. Consultar uma fonte não equivale a validar fraude, nem garante resultado completo. Dependências extras (Splink, Docling, BGE-M3, GLiNER, Prefect, etc.) continuam **candidatas de integração**, não instaladas por esse PR.

## Grok Build (código)
1. Abrir/clonar `ringuemkt-rgb/visao-tinker-bell` no Grok Build, na branch desta atualização.
2. Abrir Skills; selecionar `/forensic-intelligence-br` ou `/human-writing-os`.
3. Para MCP local autorizado:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e '.[mcp,dev]'
   VTB_DB=data/vtb.sqlite3 vtb-mcp
   ```
4. Criar missão com `mission_init`; executar `plan_public_queries`; inspecionar o plano; e depois `run_public_queries`.
5. Rodar `pytest -q` e `ruff check vtb tests` após instalar dependências.

## Grok Bot em grok.com
1. Implantar o MCP atrás de **autenticação, TLS, autorização, limite de requisições e acesso restrito ao banco**. `VTB_MCP_TRANSPORT=streamable-http`; não expor o processo cru à Internet.
2. Ir a https://grok.com/connectors → New Connector → Custom. Informar URL HTTPS do gateway MCP, completar autenticação e validar descoberta de tools.
3. Conectar GitHub pelo conector próprio para ler esta branch, se disponível no plano.
4. Colar `docs/GROK-BOT-PROMPT.md` nas instruções do Bot e pedir para salvar as duas skills privadas.
5. Testar somente com caso de demonstração e documentos públicos. Habilitar uma rotina somente após validação, com revisão humana de alertas.

Referências oficiais: https://docs.x.ai/grok/connectors e https://docs.x.ai/build/features/skills-plugins-marketplaces

## Governança obrigatória
- Sem envio automático de denúncia, publicação ou exposição de dados pessoais.
- Sem scraping de áreas restritas, bypass de autenticação ou endpoints arbitrários.
- `case_id` existente, lista de operações limitada e auditoria de cada consulta.
- `SourceHealth` ruim significa fonte indisponível, nunca inexistência.
- Criação de uma representação apenas com evidência rastreável, contraprovas e revisão humana.
