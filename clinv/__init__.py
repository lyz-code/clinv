#!/usr/bin/python3

# Copyright (C) 2019 lyz <lyz@riseup.net>
# This file is part of clinv.
#
# clinv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# clinv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with clinv.  If not, see <http://www.gnu.org/licenses/>.

# Program to maintain an inventory of assets.

from clinv.cli import load_logger, load_parser
from clinv.inventory import Inventory
from clinv.reports.active import ActiveReport
from clinv.reports.export import ExportReport
from clinv.reports.list import ListReport
from clinv.reports.monitor import MonitorReport
from clinv.reports.print import PrintReport
from clinv.reports.search import SearchReport
from clinv.reports.unassigned import UnassignedReport
from clinv.reports.unused import UnusedReport


def main():
    parser = load_parser()
    args = parser.parse_args()
    load_logger()

    inventory = Inventory(args.data_path)
    if args.subcommand not in [
        "active",
        "export",
        "generate",
        "list",
        "monitor",
        "print",
        "search",
        "unassigned",
        "unused",
    ]:
        return

    if args.subcommand == "generate":
        inventory.generate(args.resource_type)
    else:
        inventory.load()
        if args.subcommand == "search":
            SearchReport(inventory).output(args.search_string)
        elif args.subcommand == "active":
            ActiveReport(inventory).output(args.resource_type)
        elif args.subcommand == "unassigned":
            UnassignedReport(inventory).output(args.resource_type)
        elif args.subcommand == "print":
            PrintReport(inventory).output(args.search_string)
        elif args.subcommand == "list":
            ListReport(inventory).output(args.resource_type)
        elif args.subcommand == "export":
            ExportReport(inventory).output(args.export_path)
        elif args.subcommand == "monitor":
            MonitorReport(inventory).output(args.monitor_status)
        elif args.subcommand == "unused":
            UnusedReport(inventory).output()


if __name__ == "__main__":
    main()
