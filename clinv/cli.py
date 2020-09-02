import logging
import argparse
import argcomplete


def load_parser():
    """ Configure environment """

    # Argparse
    parser = argparse.ArgumentParser(
        description="DevSecOps command line asset inventory"
    )

    parser.add_argument(
        "-d",
        "--data_path",
        type=str,
        default="~/.local/share/clinv",
        help="Path to the inventory",
    )
    subparser = parser.add_subparsers(dest="subcommand", help="subcommands")

    search_parser = subparser.add_parser("search")
    search_parser.add_argument(
        "search_string", type=str, help="String used to search",
    )

    subparser.add_parser("generate")

    unassigned_parser = subparser.add_parser("unassigned")
    unassigned_parser.add_argument(
        "resource_type",
        type=str,
        nargs="?",
        help="String used to search",
        choices=[
            "all",
            "asg",
            "ec2",
            "iam_groups",
            "iam_users",
            "informations",
            "people",
            "rds",
            "route53",
            "s3",
            "services",
            "security_groups",
            "vpc",
        ],
        default="all",
    )

    list_parser = subparser.add_parser("list")
    list_parser.add_argument(
        "resource_type",
        type=str,
        help="String used to search",
        choices=[
            "asg",
            "ec2",
            "rds",
            "services",
            "iam_groups",
            "iam_users",
            "informations",
            "people",
            "projects",
            "route53",
            "s3",
            "security_groups",
            "vpc",
            None,
        ],
        nargs="?",
    )

    active_parser = subparser.add_parser("active")
    active_parser.add_argument(
        "resource_type",
        type=str,
        help="String used to search",
        default=None,
        choices=[
            "asg",
            "ec2",
            "rds",
            "services",
            "iam_groups",
            "iam_users",
            "informations",
            "people",
            "projects",
            "route53",
            "s3",
            "security_groups",
            "vpc",
            None,
        ],
        nargs="?",
    )

    export_parser = subparser.add_parser("export")
    export_parser.add_argument(
        "export_path",
        type=str,
        nargs="?",
        help="Path to export",
        default="~/.local/share/clinv/inventory.ods",
    )

    print_parser = subparser.add_parser("print")
    print_parser.add_argument(
        "search_string", type=str, help="Regexp of a Clinv resource ID",
    )

    monitored_parser = subparser.add_parser("monitored")
    monitored_parser.add_argument(
        "monitor_status",
        type=str,
        nargs="?",
        help="Monitor status of the resources",
        choices=["true", "false", "unknown",],
        default="true",
    )

    subparser.add_parser("unused")

    argcomplete.autocomplete(parser)
    return parser


def load_logger():
    logging.addLevelName(logging.INFO, "[\033[36mINFO\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31mERROR\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32mDEBUG\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33mWARNING\033[0m]")
    logging.basicConfig(level=logging.WARNING, format="  %(levelname)s %(message)s")
