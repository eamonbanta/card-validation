import re
from typing import List, Mapping

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.http.response import JsonResponse
from django.views.decorators.http import require_GET

from card_validation.errors import InvalidSetterException


# CCN should be between 12 and 19 characters, either digits or dashes,
# starting with a non-zero digit, and ending with a digit.
CCN_REGEX = re.compile(r"^\d[\d]{10,17}\d$")

MII_DETAILS_MAP = {
    "0": "ISO/TC 68 and other industry assignments",
    "1": "Airlines",
    "2": "Airlines, financial and other future industry assignments",
    "3": "Traver and Entertainment",
    "4": "Banking and Financial",
    "5": "Banking and Financial",
    "6": "Merchandising and Banking/Financial",
    "7": "Petroleum and other future industry assignments",
    "8": "Healthcare, telecommunications and other industry assignments",
    "9": "For assignment by national standards bodies"
}

# map uses a tuple key of (beginning of IIN, length of card number)
SCHEME_MAP = {
    ("4", 13): "visa",
    ("4", 16): "visa",
    ("5", 16): "mastercard",
    ("6", 16): "discover",
    ("34", 15): "american_express",
    ("37", 15): "american_express",
    ("30", 14): "diners",
    ("36", 14): "diners",
    ("38", 14): "diners",
}


class CardDetails:
    """ Stores details of a credit card number.

    The credit card number is validated using the Luhn algorithm.
    All attributes except `is_valid` will be set to `None`
    if `is_valid` is `False`.

    The following attributes are publicly readable:
        is_valid:       (bool) If card number is valid using Luhn's algorithm
        mii:            (str) Major Industry Identifier digit
        mii_details:    (str) Major Industry Identifier details
        iin:            (str) Issuer Identification Number
        scheme:         (str) visa, mastercard, etc.
        account_number: (str) Account number portion of credit card number
        checknum:       (str) Single digit used in card number validation

    No attributes can be set manually on an instance of this class.
    All attributes are set during construction.
    """
    _mii = None
    _mii_details = None
    _iin = None
    _scheme = None
    _account_number = None
    _checknum = None

    def __init__(self, ccn: str):
        # make sure that the ccn is even worth validating using a basic regex.
        if ccn and re.match(CCN_REGEX, ccn):
            ccn = self._normalize_ccn(ccn)
            self._is_valid = self._validate_ccn(ccn)
        else:
            self._is_valid = False

        if not self.is_valid:
            return

        self._mii = self._get_mii(ccn)
        self._mii_details = self._get_mii_details(ccn)
        self._iin = self._get_iin(ccn)
        self._scheme = self._get_scheme(ccn)
        self._account_number = self._get_account_number(ccn)
        self._checknum = self._get_checknum(ccn)

    def _normalize_ccn(self, ccn: str) -> List[int]:
        """ Convert CCN from string into list of integers. """
        return [int(x) for x in ccn if x.isdigit()]

    def _validate_ccn(self, ccn: List[int]) -> bool:
        """ Uses the Luhn algorithm to validate the credit card number. """

        def single_or_double(i: int, x: int):
            """ Every second digit in reverse order is doubled. """
            if i % -2 == 0:
                x *= 2
                # if a doubled digit is greater than nine, sum the digits
                if x > 9:
                    x = 1 + x % 10
            return x

        sum_of_digits = 0
        for i in range(-2, -len(ccn)-1, -1):
            sum_of_digits += single_or_double(i, ccn[i])

        checknum = 9 * sum_of_digits % 10
        return checknum == ccn[-1]

    def _get_mii(self, ccn: List[int]) -> str:
        return str(ccn[0])

    def _get_mii_details(self, ccn: List[int]) -> str:
        if not self.mii:
            self._mii = self._get_mii(ccn)
        return MII_DETAILS_MAP.get(self.mii)

    def _get_iin(self, ccn: List[int]) -> str:
        return ''.join(map(str, ccn[:6]))

    def _get_scheme(self, ccn: List[int]) -> str:
        if not self.iin:
            self._iin = self._get_iin(ccn)

        iin_first_two = self._iin[:2]

        match = SCHEME_MAP.get((iin_first_two[0], len(ccn)))
        if not match:
            match = SCHEME_MAP.get((iin_first_two, len(ccn)))
        return match

    def _get_account_number(self, ccn: List[int]) -> str:
        return ''.join(map(str, ccn[6:len(ccn)-1]))

    def _get_checknum(self, ccn: List[int]) -> str:
        return str(ccn[-1])

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def mii(self):
        return self._mii

    @property
    def mii_details(self):
        return self._mii_details

    @property
    def iin(self):
        return self._iin

    @property
    def account_number(self):
        return self._account_number

    @property
    def scheme(self):
        return self._scheme

    @property
    def checknum(self):
        return self._checknum

    # use setters to make sure that there is only one way
    # to set values: using __init__
    @is_valid.setter
    def is_valid(self):
        raise InvalidSetterException(
            'is_valid can not be set except through constructor')

    @mii.setter
    def mii(self):
        raise InvalidSetterException(
            'mii can not be set except through constructor')

    @mii_details.setter
    def mii_details(self):
        raise InvalidSetterException(
            'mii_details can not be set except through constructor')

    @iin.setter
    def iin(self):
        raise InvalidSetterException(
            'iin can not be set except through constructor')

    @scheme.setter
    def scheme(self):
        raise InvalidSetterException(
            'scheme can not be set except through constructor')

    @account_number.setter
    def account_number(self):
        raise InvalidSetterException(
            'account_number can not be set except through constructor')

    @checknum.setter
    def checknum(self):
        raise InvalidSetterException(
            'checknum can not be set except through constructor')
