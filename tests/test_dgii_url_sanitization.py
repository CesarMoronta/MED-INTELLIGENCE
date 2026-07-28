import unittest
from routes.billing import sanitize_dgii_url

class DGIIURLSanitizationTests(unittest.TestCase):
    def test_clean_url_without_changes(self):
        url = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E310000000001&RncEmisor=101000001"
        self.assertEqual(sanitize_dgii_url(url), url)

    def test_url_with_trailing_spaces_and_newlines(self):
        url = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001   \n\r "
        expected = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001"
        self.assertEqual(sanitize_dgii_url(url), expected)

    def test_url_with_encoded_spaces(self):
        url = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001%20"
        expected = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001"
        self.assertEqual(sanitize_dgii_url(url), expected)

    def test_url_with_empty_rnc_comprador_space_in_e32(self):
        url = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001&RncComprador=%20&MontoTotal=3000.00"
        expected = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E320000000001&RncComprador=&MontoTotal=3000.00"
        self.assertEqual(sanitize_dgii_url(url), expected)

    def test_domain_fc_replacement(self):
        url = "https://fc.dgii.gov.do/ConsultaTimbre?encf=E310000000001"
        expected = "https://ecf.dgii.gov.do/ConsultaTimbre?encf=E310000000001"
        self.assertEqual(sanitize_dgii_url(url), expected)

if __name__ == "__main__":
    unittest.main()
