import json
import logging
from datetime import datetime

import boto3

from logging.handlers import TimedRotatingFileHandler
from os import environ
from pathlib import Path
import click


def get_time_str() -> str:
    utc_datetime = datetime.utcnow()
    utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return utc_datetime.strftime("%Y-%m-%d-%H-%M-%S")


def get_env_list() -> list:
    """
    Return list of environments from config.json
    :return: List of environments
    """
    env_list = []
    for key, value in config.items():
        if key != "region":
            env_list.append(key)
    return env_list


def get_service_list(ref_env: str) -> list:
    """
    Return list of services from config.json referring `dvp` env
    :return: List of services
    """
    service_list = []
    for key, value in config[ref_env].items():
        if key != "region":
            service_list.append(key)
    return service_list


def log_level(level: str) -> str:
    """
    Allow the user to choose the logging level for the script.
    :param level:
    :return: log level
    """

    the_level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    return the_level[level.lower()]


project_root = Path(__file__).parent
config_file = project_root.joinpath("config.json")


def set_log_level(log_file: str):
    """
    Set Log level for the script
    :param log_file:
    :return:
    """
    global_logging_level = log_level(environ.get("LOG_LEVEL", "info"))

    logging.basicConfig(
        level=global_logging_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            TimedRotatingFileHandler(
                f"{project_root}/{log_file}.log",
                when="midnight",
                backupCount=10,
            ),
        ],
    )
    logging.getLogger("main").setLevel(global_logging_level)


def load_config_file():
    """
    Load the config file located in the root of this project.
    :return: config data
    """
    with open(config_file) as f:
        return json.load(f)


config = load_config_file()
rds_client = None


def get_an_env():
    """
    Return an environment from config.json
    :return: returns an environment
    """
    for env, value in config.items():
        if env != "region":
            return env

    raise Exception("No Environments in config file")


def get_rds_client(env):
    global rds_client
    if rds_client is None:
        rds_client = boto3.client("rds", environ.get("AWS_REGION", config[env]["region"]))

    return rds_client


def get_db_identifier(env: str, service: str) -> str:
    return config[env][service]["cluster-identifier"]


def get_rds_instance_data(env: str, service: str) -> dict:
    """
    Fetch config data of RDS instance
    :param service:
    :param env:
    :return: data of RDS instance
    Note :- This returns only the first instance
    """
    db_identity = config[env][service]["cluster-identifier"]
    db_instances = get_rds_client().describe_db_instances(DBInstanceIdentifier=db_identity)

    if len(db_instances["DBInstances"]) > 1:
        raise Exception(
            "More than one instance available for provided db-identifier")
    else:
        return db_instances["DBInstances"][0]


def get_aws_secret_name(env: str, service: str) -> str:
    """
    Returns aws secret name from config.json
    :param service:
    :param env:
    :return: aws secret
    """
    return config[env][service]["secret"]


def get_rds_snapshots(db_identifier: str):
    """
    Get the snapshots for a given RDS instance and output them in json format.

    :param db_identifier:
    :return:
    """
    try:
        snapshot_check_response = get_rds_client().describe_db_snapshots(
            DBInstanceIdentifier=db_identifier
        )

        describe_instance = get_rds_client().describe_db_instances(
            DBInstanceIdentifier=db_identifier
        )

        latest_restorable_time = ""
        for time in describe_instance["DBInstances"]:
            latest_restorable_time = time["LatestRestorableTime"]

        db_identifiers = []

        for instance in snapshot_check_response["DBSnapshots"]:
            db_identifiers.append(
                {
                    "db_identifier": instance["DBInstanceIdentifier"],
                    "snapshot_identifier": instance["DBSnapshotIdentifier"],
                    "snapshot_created_time": instance["SnapshotCreateTime"],
                }
            )

        latest_date_formatted = str(latest_restorable_time).split("+")[0]

        db_identifiers.append(
            {
                "snapshot_identifier": "latest",
                "snapshot_created_time": latest_date_formatted,
            }
        )

        return db_identifiers

    except TypeError as e:
        logging.error(f"There was an issue retrieving RDS snapshots! {e}")
        exit(1)


def closest_dates(dates, pivot, n):
    return sorted(dates, key=lambda t: abs(pivot - t))[:n]


def list_snapshot_datetime(snapshots: list):
    """
    list snapshots.
    :param snapshots: snapshots to display
    :return:
    """

    try:
        created_times = [
            datetime.strptime(
                str(t["snapshot_created_time"]).split(".", 1)[0], "%Y-%m-%d %H:%M:%S"
            )
            for t in snapshots
        ]

        closest = closest_dates(created_times, datetime.utcnow(), 25)
        close_match = [c.strftime("%Y-%m-%d %H:%M:%S") for c in closest]
        close_match.sort(reverse=True)

        return close_match

    except Exception as e:
        logging.error(e)
        exit(1)


def print_snapshots_data_and_time(db_identifier: str):
    """
    Display snapshots to the console
    :param db_identifier:
    :return:
    """
    snapshots = get_rds_snapshots(db_identifier=db_identifier)
    print()
    print("Available date and time snapshots: ")
    print("=================================")

    for dt in list_snapshot_datetime(snapshots):
        print(f"  {dt}")


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--environment",
    type=click.Choice(get_env_list(), case_sensitive=False),
    required=True,
    help="Environment the RDS instance belongs to.",
)
@click.option(
    "--service",
    type=click.Choice(get_service_list("dvp"), case_sensitive=False),
    required=True,
    help="The service the RDS instance belongs to.",
)
def fetch_snapshots_date_and_time(**kwargs):
    """
    Display snapshots with date and time
    :param kwargs:
    :return:
    """
    try:
        env = kwargs["environment"]
        service = kwargs["service"]
        db_identifier = get_db_identifier(env, service)
        print_snapshots_data_and_time(db_identifier)
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        exit(1)
