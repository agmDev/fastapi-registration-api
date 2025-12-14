class DomainError(Exception):
    pass


class UserAlreadyExists(DomainError):
    pass


class InvalidCredentials(DomainError):
    pass


class InvalidActivationCode(DomainError):
    pass


class ActivationCodeExpired(DomainError):
    pass


class UserAlreadyActive(DomainError):
    pass
