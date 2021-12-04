class Shareholder:
    def __init__(self, cik: str, name: str, title: str,
                 director: bool = False, ten_percent_owner: bool = False, officer: bool = False, other: bool = False):
        self.cik: str = cik
        self.name: str = name
        self.title: str = title
        self.director: bool = director
        self.ten_percent_owner: bool = ten_percent_owner
        self.officer: bool = officer
        self.other: bool = other
