from django.test import TestCase

class GetCardValidationViewTests(TestCase):
    def test_valid_card_number(self):
        response = self.client.get('/card-validation/5555555555554444')
        self.assertEqual(response.status_code, 200)
        expected = {
            'is_valid': True,
            'account_number': '555555444',
            'checknum': '4',
            'iin': '555555',
            'mii': '5',
            'mii_details': 'Banking and Financial',
            'scheme': 'mastercard',
        }
        self.assertEqual(response.json(), expected)

        response = self.client.get('/card-validation/4012888888881881')
        self.assertEqual(response.status_code, 200)
        expected = {
            "is_valid": True,
            "mii": "4",
            "mii_details": "Banking and Financial",
            "iin": "401288",
            "scheme": "visa",
            "account_number": "888888188",
            "checknum": "1"
        }
        self.assertEqual(response.json(), expected)

    def test_invalid_card_number_all_digits(self):
        response = self.client.get('/card-validation/1234567890123456')
        self.assertEqual(response.status_code, 200)
        expected = {
            'is_valid': False,
            'account_number': None,
            'checknum': None,
            'iin': None,
            'mii': None,
            'mii_details': None,
            'scheme': None,
        }
        self.assertEqual(response.json(), expected)

    def test_with_ccn_query_string_parameter(self):
        expected = {
            'is_valid': True,
            'account_number': '555555444',
            'checknum': '4',
            'iin': '555555',
            'mii': '5',
            'mii_details': 'Banking and Financial',
            'scheme': 'mastercard',
        }

        response = self.client.get('/card-validation?ccn=5555555555554444')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

        response = self.client.get('/card-validation/?ccn=5555555555554444')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test_with_no_ccn(self):
        response = self.client.get('/card-validation')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'<h1>Must include a credit card number.</h1>')

        response = self.client.get('/card-validation/?bbn=5555555555554444')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'<h1>Must include a credit card number.</h1>')

