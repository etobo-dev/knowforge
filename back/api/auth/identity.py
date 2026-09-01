from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedIdentity:
    cognito_sub: str
    email: str | None
