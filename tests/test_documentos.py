import unittest

from vtb.documentos import analisar, host_ok


class DocumentoTest(unittest.TestCase):
    def test_host_oficial(self):
        self.assertTrue(host_ok("https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"))
        self.assertFalse(host_ok("http://pncp.gov.br/x"))
        self.assertFalse(host_ok("https://exemplo.com/doc.pdf"))

    def test_analise_nao_afirma_improbidade(self):
        path = "/tmp/doc-oficial.txt"
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Contrato 123 valor 10")
        exame = analisar(path, "https://pncp.gov.br/doc", ["Contrato"])
        self.assertFalse(exame["improbidade_afirmavel"])
        self.assertEqual(exame["label"], "ANOMALY_FOR_VERIFICATION")
        self.assertTrue(exame["ocorrencias"])
