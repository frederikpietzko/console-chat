from pprint import pprint as print
from . import settings


def log(message: str):
    if settings.DEBUG:
        print(message)
