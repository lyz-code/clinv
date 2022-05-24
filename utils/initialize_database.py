"""Script to initialize the database."""

import logging
import sys

from repository_orm import load_repository

from clinv.entrypoints import load_logger
from clinv.model import Authentication, NetworkAccess

log = logging.getLogger(__name__)
load_logger()

try:
    database_url = sys.argv[1]
except IndexError:
    log.error(
        "Please specify the database url as the first argument. "
        "For example: tinydb://~/.local/share/clinv/database.tinydb"
    )
    sys.exit(1)

repo = load_repository(database_url, search_exception=False)

network_accesses = [
    NetworkAccess(
        id_="net_001",  # type: ignore
        name="internet",
        description="Services are exposed to the whole internet.",
        security_value=0,
    ),
    NetworkAccess(
        id_="net_002",  # type: ignore
        name="intranet",
        description="Services are exposed to the internal network only.",
        security_value=100,
    ),
    NetworkAccess(
        id_="net_003",  # type: ignore
        name="airgap",
        description="Services are in a network isolated device.",
        security_value=200,
    ),
]

authentications = [
    Authentication(
        id_="auth_001",  # type: ignore
        name="Open",
        description=(
            "There is no authorisation or authentication required to access the service"
        ),
        security_value=0,
    ),
    Authentication(
        id_="auth_002",  # type: ignore
        name="2FA hardware key",
        description=(
            "Two-Factor-Authentication by hardware key. It's security is greater than "
            "the 2FA application code because it's harder to be obtained by an attacker"
            ". Also the user can save the seed in more places that could be leaked."
        ),
        security_value=10,
    ),
    Authentication(
        id_="auth_003",  # type: ignore
        name="2FA application code",
        description="Two-Factor-Authentication by application code.",
        security_value=8,
    ),
    Authentication(
        id_="auth_004",  # type: ignore
        name="Webserver Basic Authorisation",
        description=(
            "Builtin webserver basic authorisation, the low security value reflects "
            "the fact that they are usually not rotated frequently because it's hard "
            "to do by default."
        ),
        security_value=3,
    ),
    Authentication(
        id_="auth_005",  # type: ignore
        # B105: We're not leaking any password
        name="User and Password",  # nosec: B105
        description=(
            "Service protected behind an user and password stored locally in the "
            "application. The security value is smaller than other solutions because "
            "the security of an application is not as well tested and maintained as "
            "for example LDAP or OAuth applications."
        ),
        security_value=5,
    ),
    Authentication(
        id_="auth_006",  # type: ignore
        name="SSL Client Certificate",
        description=(
            "Service requires the user's SSL certificate to accept requests, it's "
            "security value is similar to the 2fa application code because leaking the "
            'certificate is "easier" than for example a 2fa hardware key, as it is'
            "stored in the device."
        ),
        security_value=8,
    ),
    Authentication(
        id_="auth_007",  # type: ignore
        name="LDAP",
        description=(
            "The service delegates authentication and authorisation to an external "
            "LDAP server. It's security is smaller than the OAuth because it's a "
            "more complex service with greater exposure."
        ),
        security_value=8,
    ),
    Authentication(
        id_="auth_008",  # type: ignore
        name="OAuth",
        description=(
            "The service delegates authentication and authorisation to an external "
            "OAuth server."
        ),
        security_value=10,
    ),
    Authentication(
        id_="auth_009",  # type: ignore
        name="API Key",
        description=(
            "The service delegates authentication and authorisation to an external "
            "OAuth server."
            "Service protected behind a token stored locally in the "
            "application. The security value is smaller than other solutions because "
            "the security of an application is not as well tested and maintained as "
            "for example LDAP or OAuth applications. It's greater than the user and "
            "password though as it's easier to programmatically rotate and it's harder "
            "to bruteforce."
        ),
        security_value=6,
    ),
    Authentication(
        id_="auth_010",  # type: ignore
        name="SSH Keys",
        description=(
            "Service requires the user's SSH certificate to accept requests, it's "
            "security value is similar to the 2fa application code because leaking the "
            'certificate is "easier" than for example a 2fa hardware key, as it is'
            "stored in the device."
        ),
        security_value=8,
    ),
]

initial_load = [
    (NetworkAccess, network_accesses),
    (Authentication, authentications),
]

for model, elements in initial_load:
    model_name = model.schema()["title"]  # type: ignore
    if len(repo.all(model)) > 0:  # type: ignore
        log.warning(
            f"There are already {model_name} resources "
            "in the database, skipping the initial load of these elements."
        )
        continue
    log.info(f"Importing the {model_name} elements.")
    repo.add(elements)  # type: ignore
    repo.commit()
