# Tinker Bell MCP Server

O Tinker Bell pode ser conectado a clientes compatíveis com o **Model Context Protocol (MCP)**. O servidor expõe as capacidades defensivas do runtime como ferramentas estruturadas, sem permitir execução arbitrária de shell.

## Princípios de segurança

O servidor trabalha com casos locais e dados autorizados ou públicos. Ele não contorna autenticação, não faz enumeração de contas, não executa comandos recebidos pela IA e não transforma red flags, matches ou anomalias em prova de crime. Toda conclusão sensível exige evidência, revisão humana e os gates do caso.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[mcp]'
```

O banco utilizado pelo servidor é controlado pela variável `VTB_DB`. Se ela não existir, o padrão é `data/vtb.sqlite3` dentro do diretório de execução.

```bash
export VTB_DB=/caminho/seguro/data/vtb.sqlite3
```

## Execução local por stdio

Este é o modo recomendado para Claude Desktop, Cursor, Cline, Windsurf e clientes locais semelhantes. O cliente inicia o processo e conversa com ele por entrada e saída padrão.

```bash
VTB_DB=/caminho/seguro/data/vtb.sqlite3 vtb-mcp
```

Exemplo genérico de configuração JSON:

```json
{
  "mcpServers": {
    "tinker-bell": {
      "command": "/caminho/para/.venv/bin/vtb-mcp",
      "args": [],
      "env": {
        "VTB_DB": "/caminho/seguro/data/vtb.sqlite3"
      }
    }
  }
}
```

## Execução HTTP

Para um cliente remoto ou uma implantação em servidor, o SDK MCP oferece transportes HTTP. O processo deve ficar atrás de autenticação, TLS, firewall e controle de acesso por usuário antes de ser exposto à internet.

```bash
VTB_MCP_TRANSPORT=streamable-http VTB_DB=/caminho/seguro/data/vtb.sqlite3 vtb-mcp
```

O endpoint e os requisitos exatos de autenticação dependem da versão do SDK e do cliente MCP utilizado. Não publique o processo diretamente sem uma camada de identidade e autorização.

## Ferramentas expostas

| Ferramenta | Função |
|---|---|
| `source_health` | Classifica a saúde de uma fonte HTTP sem converter bloqueio em ausência. |
| `mission_init` | Cria um caso com pergunta e escopo. |
| `mission_status` | Consulta o estado do caso. |
| `mission_transition` | Avança somente por transição válida. |
| `case_export` | Exporta missão, fontes, evidências, buscas, ferramentas e auditoria. |
| `case_bundle` | Cria um pacote `vtb-case-bundle-v1` com JSON determinístico e manifesto SHA-256. |
| `case_bundle_verify` | Verifica o manifesto e detecta adulteração do pacote. |
| `case_audit` | Lista eventos append-only do caso. |
| `manifest_verify` | Verifica SHA-256 e tamanho de artefatos preservados. |
| `evaluate_red_flags` | Executa regras locais determinísticas como sinais para verificação. |
| `triage_signals` | Calcula prioridade de revisão, nunca probabilidade de culpa. |
| `red_flag_catalog` | Lista regras declarativas, campos exigidos e estado de implementação. |
| `next_best_queries` | Prioriza consultas candidatas por ganho informacional e custo. |
| `preserve_navigation_snapshot` | Preserva conteúdo fornecido pelo cliente com URL e SHA-256; não navega na internet. |

O servidor não expõe uma ferramenta genérica de requisição HTTP ou execução de código. Novos conectores devem ser adicionados como adapters explicitamente revisados, com timeout, rate limit, schema, preservação, proveniência e testes.

`preserve_navigation_snapshot` é deliberadamente passiva: a IA ou o cliente deve fornecer o conteúdo que já obteve de forma autorizada. O Tinker Bell grava o conteúdo, calcula hash e cria manifesto, mas não visita URLs nem tenta contornar bloqueios.

## Exemplo de fluxo com uma IA

1. A IA cria uma missão com `mission_init`.
2. Define o escopo e avança o estado com `mission_transition`.
3. Usa adapters aprovados do Tinker Bell para coletar dados autorizados.
4. Registra evidências e preserva os artefatos no CaseStore.
5. Usa `evaluate_red_flags` e `triage_signals` para priorizar revisão.
6. Consulta `case_audit` e `case_export` antes de produzir um relatório.
7. Mantém explícitas as lacunas, contradições, incertezas e explicações alternativas.

## Limites atuais

O MCP é uma camada de interoperabilidade. Ele não cria automaticamente uma plataforma multiusuário, não fornece autenticação remota, não substitui o banco de produção e não libera todos os adapters nacionais. Para produção, adicione RBAC/ABAC, isolamento por caso, criptografia, backup, retenção, logs externos e revisão jurídica/privacidade.
