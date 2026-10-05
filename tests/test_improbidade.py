import unittest

from vtb.improbidade import avaliar, bloco


class ImprobidadeTest(unittest.TestCase):
    def test_culpa_nao_vira_improbidade(self):
        exame = avaliar({"ato_concreto": "contrato", "so_culpa_grave": True, "rotulo": "improbidade"})
        self.assertFalse(exame["improbidade_afirmavel"])
        self.assertIn("culpa_nao_basta", exame["faltas"])
        self.assertIn("rotulo_vedado", exame["faltas"])
        self.assertIn("Tema 1199", bloco({"ato_concreto": "contrato"}))


if __name__ == "__main__":
    unittest.main()
