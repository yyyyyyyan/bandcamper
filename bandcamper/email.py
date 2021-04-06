class OneSecMail:
    API_URL = "https://www.1secmail.com/api/v1/"
    DOMAINS = [
        "1secmail.com",
        "1secmail.net",
        "1secmail.org",
        "esiix.com",
        "wwjmp.com",
    ]

    def __init__(self, user, domain):
        self.user = user
        self.domain = domain

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        if value not in self.DOMAINS:
            raise ValueError(f"{value} is not an allowed domain")
        self._domain = value
