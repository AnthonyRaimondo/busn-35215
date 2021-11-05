class Shareholder:
    def __init__(self, cik, name, title, director = False, ten_percent_owner = False, officer = False, other = False):
        self.cik: str = cik
        self.name: str = name
        self.title: str = title
        self.director: bool = director
        self.ten_percent_owner: bool = ten_percent_owner
        self.officer: bool = officer
        self.other: bool = other
