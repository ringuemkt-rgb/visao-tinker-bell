#!/usr/bin/env python3
"""
Visão Tinker Bell — Motor de Red Flags
Adaptado do Monitor de Gravata (regras públicas e determinísticas).
Avalia sinais objetivos. Nunca gera acusação.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    rule_id: str
    nome: str
    categoria: str
    severidade: str
    descricao: str
    fonte: str
    evidencia: Dict[str, Any] = field(default_factory=dict)
    mensagem: str = ""


class RedFlagsEngine:
    def __init__(self, rules_path: Optional[Path] = None):
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "rules" / "red_flags.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = {r["id"]: r for r in json.load(f)}

    def evaluate(self, context: Dict[str, Any]) -> List[Finding]:
        findings: List[Finding] = []
        for rule_id, rule in self.rules.items():
            if not rule.get("implementada"):
                continue
            try:
                if self._match(rule, context):
                    findings.append(
                        Finding(
                            rule_id=rule_id,
                            nome=rule["nome"],
                            categoria=rule["categoria"],
                            severidade=rule["severidade"],
                            descricao=rule["descricao"],
                            fonte=rule["fonte"],
                            evidencia={
                                k: context.get(k) for k in rule.get("dados_necessarios", [])
                            },
                            mensagem=self._build_message(rule, context),
                        )
                    )
            except Exception:
                continue
        return findings

    def _match(self, rule: Dict, ctx: Dict) -> bool:
        rid = rule["id"]

        if rid == "contrato-valor-global-elevado":
            return float(ctx.get("valorGlobal") or 0) >= 10_000_000

        if rid == "contrato-valor-muito-elevado":
            return float(ctx.get("valorGlobal") or 0) >= 100_000_000

        if rid == "contrato-fruto-de-adesao":
            return bool(ctx.get("frutoAdesao"))

        if rid == "contrato-multiplas-retificacoes":
            return int(ctx.get("numeroRetificacao") or 0) >= 3

        if rid == "contrato-vigencia-superior-5-anos":
            dias = self._days_between(ctx.get("dataVigenciaInicio"), ctx.get("dataVigenciaFim"))
            return dias is not None and dias > 365 * 5

        if rid == "fornecedor-cnpj-recem-aberto":
            dias = self._days_between(ctx.get("data_inicio_atividade"), ctx.get("dataAssinatura"))
            return dias is not None and dias < 365

        if rid == "fornecedor-cnpj-muito-recente":
            dias = self._days_between(ctx.get("data_inicio_atividade"), ctx.get("dataAssinatura"))
            return dias is not None and dias < 180

        if rid == "fornecedor-situacao-cadastral-irregular":
            sit = (ctx.get("descricao_situacao_cadastral") or ctx.get("situacao") or "").upper()
            return bool(sit) and sit != "ATIVA"

        if rid == "fornecedor-sancionado-ceis-cnep":
            return (ctx.get("count_ceis") or 0) + (ctx.get("count_cnep") or 0) > 0

        if rid == "fornecedor-capital-social-incompativel":
            valor = float(ctx.get("valorGlobal") or 0)
            capital = float(ctx.get("capital_social") or 0)
            return valor >= 500_000 and capital > 0 and (capital / valor) < 0.01

        if rid == "empresa-capital-social-simbolico-com-contratos":
            capital = float(ctx.get("capital_social") or 0)
            soma = float(ctx.get("soma_contratos") or 0)
            return capital <= 10_000 and soma > 1_000_000

        if rid == "fornecedor-mei-contrato-acima-limite":
            mei = bool(ctx.get("opcao_pelo_mei") or ctx.get("mei"))
            valor = float(ctx.get("valorGlobal") or 0)
            return mei and valor > 81_000

        if rid == "fornecedor-outra-uf-servico-local":
            if not ctx.get("servico_local"):
                return False
            uf_e = (ctx.get("uf_empresa") or "").upper()
            uf_o = (ctx.get("uf_orgao") or "").upper()
            return bool(uf_e and uf_o and uf_e != uf_o)

        if rid == "dispensa-emergencial":
            mod = ctx.get("modalidadeId")
            amparo = (ctx.get("amparoLegal") or "").lower()
            return mod in (8, "8") or any(x in amparo for x in ("emerg", "calamidade"))

        if rid == "dispensa-valor-alto":
            mod = ctx.get("modalidadeId")
            valor = float(ctx.get("valorTotalEstimado") or ctx.get("valorGlobal") or 0)
            return mod in (8, 9, "8", "9") and valor >= 1_000_000

        if rid == "licitacao-prazo-proposta-curto":
            dias = self._days_between(
                ctx.get("dataPublicacaoPncp"), ctx.get("dataEncerramentoProposta")
            )
            return dias is not None and dias < 8

        if rid == "ceap-fornecedor-dominante":
            return float(ctx.get("share_top1_fornecedor") or 0) > 0.4

        if rid == "ceap-divulgacao-acima-de-50":
            return float(ctx.get("share_divulgacao") or 0) > 0.5

        if rid == "ceap-nota-unica-elevada":
            return float(ctx.get("max_valor_liquido_ceap") or 0) > 20_000

        if rid == "ceap-combustivel-elevado":
            return float(ctx.get("media_mensal_combustivel") or 0) > 6_000

        if rid == "candidato-patrimonio-salto":
            atual = float(ctx.get("totalDeBens_atual") or 0)
            anterior = float(ctx.get("totalDeBens_anterior") or 0)
            return anterior > 0 and (atual / anterior) > 2

        if rid == "candidato-patrimonio-salto-extremo":
            atual = float(ctx.get("totalDeBens_atual") or 0)
            anterior = float(ctx.get("totalDeBens_anterior") or 0)
            return anterior > 0 and (atual / anterior) > 5

        if rid == "candidato-sem-bens-declarados":
            return float(ctx.get("totalDeBens") or 0) == 0

        if rid == "candidato-processos-cassacao":
            return int(ctx.get("count_processos_cassacao") or 0) > 0

        if rid == "hhi-fornecedores-concentrado":
            return float(ctx.get("hhi") or 0) > 2500

        return False

    def _days_between(self, d1, d2) -> Optional[int]:
        try:
            if isinstance(d1, str):
                d1 = datetime.fromisoformat(d1.replace("Z", "")).date()
            if isinstance(d2, str):
                d2 = datetime.fromisoformat(d2.replace("Z", "")).date()
            if isinstance(d1, date) and isinstance(d2, date):
                return abs((d2 - d1).days)
        except Exception:
            pass
        return None

    def _build_message(self, rule: Dict, ctx: Dict) -> str:
        return f"[SINAL] {rule['nome']} (severidade: {rule['severidade']}) — {rule['descricao']}"


def load_engine() -> RedFlagsEngine:
    return RedFlagsEngine()


if __name__ == "__main__":
    engine = load_engine()
    print(f"Regras carregadas: {len(engine.rules)}")
    exemplo = {
        "valorGlobal": 15_000_000,
        "descricao_situacao_cadastral": "BAIXADA",
        "capital_social": 1_000,
        "data_inicio_atividade": "2025-01-15",
        "dataAssinatura": "2025-06-01",
        "totalDeBens": 0,
        "totalDeBens_atual": 5_000_000,
        "totalDeBens_anterior": 800_000,
        "hhi": 3200,
        "count_ceis": 1,
    }
    findings = engine.evaluate(exemplo)
    print(f"Encontrados {len(findings)} sinais:")
    for f in findings:
        print(f"  - [{f.severidade.upper()}] {f.nome}")
