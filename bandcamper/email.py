from random import choice as random_choice
from uuid import uuid4

import requests


class OneSecMail:
    API_URL = "https://www.1secmail.com/api/v1/"
    DOMAINS = [
        "1secmail.com",
        "1secmail.net",
        "1secmail.org",
        "esiix.com",
        "wwjmp.com",
    ]

    def __init__(self, user, domain, **requests_kwargs):
        self.user = user
        self.domain = domain
        self.requests_kwargs = requests_kwargs

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        if value not in self.DOMAINS:
            raise ValueError(f"{value} is not an allowed domain")
        self._domain = value

    @classmethod
    def get_random_mailbox(cls, **requests_kwargs):
        response = requests.get(
            cls.API_URL, params={"action": "genRandomMailbox"}, **requests_kwargs
        )
        user, domain = response.json()[0].split("@")
        return cls(user, domain, **requests_kwargs)

    @classmethod
    def generate_random_mailbox(cls, **requests_kwargs):
        user = uuid4().hex
        domain = random_choice(cls.DOMAINS)
        return cls(user, domain, **requests_kwargs)
