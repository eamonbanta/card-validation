import logging
import re
from typing import List, Mapping

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseBadRequest
from django.http.response import JsonResponse
from django.views.decorators.http import require_GET

from card_validation.card_details import CardDetails


logger = logging.getLogger('django')


@require_GET
def get_card_validation(request: WSGIRequest, ccn: str = None) -> JsonResponse:
    logger.info("GET /card-validation")

    if not ccn:
        ccn = request.GET.get("ccn")
        if not ccn:
            logger.info("No credit card number provided; raise 404")
            html = "<h1>Must include a credit card number.</h1>"
            return HttpResponseBadRequest(html)

    card_details = CardDetails(ccn)
    log_valid_string = "valid" if card_details.is_valid else "invalid"
    logger.info("Provided credit card number was {}".format(log_valid_string))
    return JsonResponse(__json(card_details))


def __json(card_details: CardDetails = None) -> Mapping:
    is_valid = bool(card_details and card_details.is_valid)
    json_dict = {"is_valid": is_valid}

    attributes = [
        "mii", "mii_details", "iin",
        "scheme", "account_number", "checknum",
    ]

    if is_valid:
        for attr in attributes:
            json_dict[attr] = getattr(card_details, attr)
    else:
        for attr in attributes:
            json_dict[attr] = None

    return json_dict
