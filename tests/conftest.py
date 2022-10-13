"""Store the classes and fixtures used throughout the tests."""

import os
from typing import Any, Dict, Generator

import boto3
import pytest
from moto import mock_autoscaling, mock_ec2, mock_iam, mock_rds, mock_route53, mock_s3
from py._path.local import LocalPath
from repository_orm import FakeRepository, TinyDBRepository

from clinv.adapters.fake import FakeSource
from clinv.config import Config


@pytest.fixture(name="config")
def fixture_config(db_tinydb: str) -> Config:
    """Configure the Config object for the tests."""
    # Once https://github.com/lincolnloop/goodconf/issues/10 is solved prepend
    # the environment variables with the program prefix
    # to configure it use os.environ["DEBUG"] = 'True'
    os.environ["CLINV_CONFIG_PATH"] = "tests/assets/config.yaml"
    os.environ["DATABASE_URL"] = db_tinydb
    os.environ["SOURCES"] = '["risk"]'
    config = Config()
    config.load("tests/assets/config.yaml")
    return config


@pytest.fixture(name="db_tinydb")
def db_tinydb_(tmpdir: LocalPath) -> str:
    """Create the TinyDB database url.

    Returns:
        database_url: Url used to connect to the database.
    """
    # ignore: Call of untyped join function in typed environment.
    # Until they give typing information there is nothing else to do.
    tinydb_file_path = str(tmpdir.join("tinydb.db"))  # type: ignore

    tinydb_url = f"tinydb:///{tinydb_file_path}"

    return tinydb_url


# Adapter Fixtures


@pytest.fixture(name="repo")
def repo_() -> Generator[FakeRepository, None, None]:
    """Configure a FakeRepository instance"""
    repo = FakeRepository()

    yield repo

    repo.close()


@pytest.fixture(name="repo_tinydb")
def repo_tinydb_(db_tinydb: str) -> Generator[TinyDBRepository, None, None]:
    """Configure a TinyDBRepository instance"""
    repo = TinyDBRepository(db_tinydb)

    yield repo

    repo.close()


@pytest.fixture(name="source")
def source_() -> FakeSource:
    """Configure a FakeSource instance."""
    return FakeSource()


# AWS fixtures
@pytest.fixture()
def _aws_credentials() -> None:
    """Mock the AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(name="ec2")
def ec2_(_aws_credentials: None) -> Any:
    """Configure the boto3 EC2 client."""
    with mock_ec2():
        yield boto3.client("ec2", region_name="us-east-1")


@pytest.fixture(name="rds")
def rds_(_aws_credentials: None) -> Any:
    """Configure the boto3 RDS client."""
    # Until https://github.com/boto/botocore/issues/2705 is closed
    os.environ["BOTO_DISABLE_COMMONNAME"] = "true"
    with mock_rds():
        yield boto3.client("rds", region_name="us-east-1")


@pytest.fixture(name="s3_mock")
def s3_(_aws_credentials: None) -> Any:
    """Configure the boto3 S3 client."""
    with mock_s3():
        yield boto3.client("s3")


@pytest.fixture(name="route53")
def route53_(_aws_credentials: None) -> Any:
    """Configure the boto3 Route53 client."""
    with mock_route53():
        yield boto3.client("route53")


@pytest.fixture(name="autoscaling")
def autoscaling_(_aws_credentials: None) -> Any:
    """Configure the boto3 Autoscaling Group client."""
    with mock_autoscaling():
        yield boto3.client("autoscaling", region_name="us-east-1")


@pytest.fixture(name="iam")
def iam_(_aws_credentials: None) -> Any:
    """Configure the boto3 IAM client."""
    with mock_iam():
        yield boto3.client("iam")


# R0913: too many arguments, but it's how it has to be.
@pytest.fixture(name="all_aws")
def all_aws_(  # noqa: R0913
    ec2: Any, autoscaling: Any, rds: Any, s3_mock: Any, route53: Any, iam: Any
) -> Dict[str, Any]:
    """Prepare all aws mocks."""
    return {
        "autoscaling": autoscaling,
        "ec2": ec2,
        "iam": iam,
        "rds": rds,
        "route53": route53,
        "s3": s3_mock,
    }
