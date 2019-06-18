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
from clinv.clinv import Clinv


def main():
    parser = load_parser()
    args = parser.parse_args()
    load_logger()

    clinv = Clinv(args.inventory_path)
    if args.subcommand == 'search':
        clinv.load_inventory()
        clinv.print_ec2(args.search_string)
    elif args.subcommand == 'generate':
        clinv._fetch_ec2()
        clinv.save_inventory()


if __name__ == "__main__":
    main()
