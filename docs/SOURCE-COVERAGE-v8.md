# Cobertura nacional de fontes — VTB v8

O catálogo `config/sources_br_v8.yaml` organiza fontes por **domínio**, não promete que todas estejam disponíveis em toda execução.

## Domínios

- procurement / contracts
- budget / payments / transfers
- corporate
- electoral / assets
- control / judicial
- legislative
- sanctions / PEP
- price intelligence

## Regra de autoridade

- **A**: fonte pública oficial/primária ou base oficial estruturada;
- **B**: instituição pública/acadêmica de alta autoridade;
- **C**: derivada/enrichment/índice confiável;
- **D**: pista informal/comercial/social.

## Cobertura não é disponibilidade

Para cada missão, registrar `SourceHealth`. Uma fonte pode existir no catálogo e estar `BLOCKED`, `TIMEOUT`, `DEGRADED` ou `AUTH_REQUIRED`. Nessas condições, zero resultado nunca equivale a inexistência.

## Casos municipais

O roteador deve combinar fontes nacionais com as fontes locais do ente e o respectivo Tribunal de Contas. Para Bahia, por exemplo, o plano pode incluir TCM-BA/TCE-BA, MP-BA, Diário Oficial, transparência municipal, PNCP e fontes federais pertinentes.
