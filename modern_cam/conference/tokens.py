from django.core import signing

from .models import Submission


def submission_from_token(token, expected_action):
    try:
        return Submission.from_signed_token(token, expected_action)
    except (Submission.DoesNotExist, signing.BadSignature, signing.SignatureExpired):
        return None
