"""Migrate the data from user_data.yaml and source_data.yaml to database.tinydb.

You'll probably need to install the dependencies with:

pip install ruyaml

The paths to the files are assumed to be the default, if you've changed them,
search this file for `~/.local/share/clinv` and change them accordingly.

The script only migrates the user data, as it's assumed that the source data is
outdated and it's easier to fetch from the sources than migrate it. That means that
you'll loose the data of the AWS terminated resources.
"""

import logging
import os
import sys
from contextlib import suppress
from typing import Any, Dict, List

from pydantic import ValidationError
from repository_orm import EntityNotFoundError, load_repository
from rich.logging import RichHandler
from ruamel.yaml import YAML  # type: ignore
from ruamel.yaml.scanner import ScannerError

from clinv import EC2, Entity
from clinv.model import (
    ASG,
    EC2,
    MODELS,
    RDS,
    S3,
    VPC,
    IAMGroup,
    IAMUser,
    Information,
    People,
    Project,
    Route53,
    Service,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

repo = load_repository(
    models=MODELS, database_url="tinydb://~/.local/share/clinv/database.tinydb"
)


def load_yaml(file_path: str) -> Dict["str", Any]:
    """Load the data from a yaml."""
    try:
        with open(os.path.expanduser(file_path), "r") as f:
            try:
                data = YAML().load(f)
            except ScannerError as e:
                log.error(
                    "Error parsing yaml of configuration file "
                    "{}: {}".format(
                        e.problem_mark,
                        e.problem,
                    )
                )
                sys.exit(1)
    except FileNotFoundError:
        log.error(f"Error opening configuration file {file_path}")
        sys.exit(1)
    return data


def _join_yaml_information(
    source_: Any, user: Any, resource_type: str, id_: str
) -> Any:
    """Join the data from the user_data.yaml and source_data.yaml in one dictionary."""
    source_data = {}
    with suppress(KeyError):
        if resource_type == "ec2":
            for region in source_["ec2"]:
                for group in source_["ec2"][region]:
                    for instance in group["Instances"]:
                        if instance["InstanceId"] == id_:
                            source_data = instance
        elif resource_type == "rds":
            for region in source_["rds"]:
                for instance in source_["ec2"][region]:
                    if instance["DbiResourceId"] == id_:
                        source_data = instance
        else:
            source_data = source[resource_type][id_]
    return {**source_data, **user[resource_type][id_]}


def _adapt_new_id(id_: str, resource_type: str) -> str:
    """Return the id in the new format.

    In this version the convention of the ids of some resources has changed.
    """
    new_ids = {  # noqa: ECE001
        "iam_groups": f"iamg-{id_.split('/')[-1].lower()}",
        "iam_users": f"iamu-{id_.split('/')[-1].lower()}",
        "s3": f"s3-{id_.lower()}",
    }
    try:
        return new_ids[resource_type]
    except KeyError:
        return id_


def _adapt_environment(data: Any) -> List[str]:
    """Transform the environment key to the new list."""
    with suppress(KeyError):
        environment = data["environment"]
        if environment in ["production", "staging", "testing"]:
            return [environment.capitalize()]
    return []


def _build_model(id_: str, resource_type: str, data: Any) -> Entity:
    """Build the models with the old data."""
    if resource_type == "asg":
        entity: Any = ASG(
            id_=id_,
            description=data["description"],
            state=data["state"],
            min_size=data["MinSize"],
            max_size=data["MaxSize"],
            desired_size=data["DesiredCapacity"],
            region=data["region"],
            healthcheck=data["HealthCheckType"],
        )
    elif resource_type == "ec2":
        # Set state
        try:
            state = data["State"]["Name"]
            if state == "running":
                state = "active"
        except KeyError:
            raise EntityNotFoundError("Not enough data to add the instance")

        try:
            entity = EC2(
                id_=id_,
                ami=data["ImageId"],
                description=data["description"],
                environment=_adapt_environment(data),
                region=data["region"],
                start_date=data["LaunchTime"],
                size=data["InstanceType"],
                vpc=data["VpcId"],
                state=state,
            )
        except KeyError:
            raise EntityNotFoundError("Not enough data to add the instance")

        # Set monitor
        with suppress(KeyError):
            if isinstance(data["monitor"], bool):
                entity.monitor = data["monitor"]
    elif resource_type == "iam_groups":
        entity = IAMGroup(
            id_=id_,
            description=data["description"],
            name=data["name"],
            state=data["state"],
            arn=data["arn"],
            users=[_adapt_new_id(user, "iam_group") for user in data["desired_users"]],
        )
    elif resource_type == "iam_users":
        entity = IAMUser(
            id_=id_,
            description=data["description"],
            name=data["name"],
            state=data["state"],
            arn=data["arn"],
        )
    elif resource_type == "informations":
        entity = Information(
            id_=id_,
            description=data["description"],
            name=data["name"],
            state=data["state"],
            personal_data=data["personal_data"],
            responsible=data["responsible"],
        )
    elif resource_type == "people":
        entity = People(
            id_=id_,
            description=data["description"],
            name=data["name"],
            state=data["state"],
            email=data["email"],
            iam_user=_adapt_new_id(data["iam_user"], "iam_user"),
        )
    elif resource_type == "projects":
        for key in ["aliases", "informations", "people", "services"]:
            if resource_data[key] == "tbd":
                resource_data[key] = ["tbd"]
            elif not isinstance(resource_data[key], list):
                resource_data[key] = []
        entity = Project(
            id_=id_,
            description=data["description"],
            name=data["name"],
            state=data["state"],
            aliases=data["aliases"],
            informations=data["informations"],
            services=data["informations"],
            people=data["people"],
        )
    elif resource_type == "rds":
        try:
            state = data["DBInstanceStatus"]
        except KeyError:
            raise EntityNotFoundError("Not enough data to add the instance")
        if state == "available":
            state = "active"
        else:
            state = "terminated"

        endpoint = f"{data['Endpoint']['Address']}:{data['Endpoint']['Port']}"
        entity = RDS(
            id_=id_,
            description=data["description"],
            region=data["region"],
            environment=_adapt_environment(data),
            size=data["DBInstanceClass"],
            state=state,
            vpc=data["DBSubnetGroup"]["VpcId"],
            endpoint=endpoint,
            start_date=data["InstanceCreateTime"],
            engine=f"{data['Engine']} {data['EngineVersion']}",
        )
    elif resource_type == "route53":
        entity = Route53(
            id_=id_,
            description=data["description"],
            state=data["state"],
            hosted_zone=id_.split("-")[0],
            type_=id_.split("-")[-1],
        )
        with suppress(KeyError):
            if isinstance(data["monitor"], bool):
                entity.monitor = data["monitor"]
    elif resource_type == "s3":
        try:
            entity = S3(
                id_=id_,
                description=data["description"],
                state=data["state"],
                environment=_adapt_environment(data),
                start_date=data["CreationDate"],
                public_read=data["desired_permissions"]["read"] == "public",
                public_write=data["desired_permissions"]["write"] == "public",
            )
        except KeyError:
            raise EntityNotFoundError("Not enough data to add the instance")
    elif resource_type == "services":
        entity = Service(
            id_=id_,
            name=data["name"],
            description=data["description"],
            state=data["state"],
            access=data["access"],
            responsible=data["responsible"],
            resources=[],
            users=data["users"],
            authentication=[],
        )
        with suppress(KeyError):
            for key in ["dependencies", "informations"]:
                if data[key] == "tbd" or data[key] is None:
                    continue
                else:
                    setattr(entity, key, data[key])
        with suppress(KeyError, TypeError):
            for aws_type in data["aws"]:
                for resource_id in data["aws"][aws_type]:
                    entity.resources.append(_adapt_new_id(resource_id, aws_type))

        with suppress(KeyError):
            authentication = data["authentication"]["method"]
            if authentication is None:
                pass
            elif isinstance(authentication, list):
                entity.authentication += authentication
            else:
                entity.authentication.append(authentication)
    elif resource_type == "vpc":  # noqa: SIM106
        entity = VPC(
            id_=id_,
            description=data["description"],
            state=data["state"],
            cidr=data["CidrBlock"],
            region=data["region"],
        )
    else:
        raise ValueError(
            "I don't know how to translate {resource_type} to the new models"
        )
    return entity


log.info("Loading old data.")
source = load_yaml("~/.local/share/clinv/source_data.yaml")
user = load_yaml("~/.local/share/clinv/user_data.yaml")

log.info("Translating old data to the new format.")
for resource_type in user.keys():
    # for resource_type in track(user.keys(), description="Resource types"):
    if resource_type == "security_groups":
        continue
    for id_, _ in user[resource_type].items():
        log.info(id_)
        resource_data = _join_yaml_information(source, user, resource_type, id_)
        if resource_type in ["iam_groups", "iam_users"]:
            resource_data["arn"] = id_
        new_id = _adapt_new_id(id_, resource_type)

        try:
            entity = _build_model(new_id, resource_type, resource_data)
        except ValidationError as error:
            __import__("pdb").set_trace()  # XXX BREAKPOINT
            print(str(error))
        except EntityNotFoundError:
            continue
        repo.add(entity)
log.info("Saving data in the repository")
repo.commit()
