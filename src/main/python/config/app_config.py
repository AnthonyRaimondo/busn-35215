import os


class AppConfig:
    SEC_API_KEY: str
    SEC_USER_AGENT: str

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            value = env.get(field)
            if value is None:
                raise Exception(f"{field} environment variable must be set")

            self.__setattr__(field, value)

    def __repr__(self):
        return str(self.__dict__)


# Allow for importing of environment variables elsewhere
Config = AppConfig(os.environ)
