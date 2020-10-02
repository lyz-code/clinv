[![Actions Status](https://github.com/lyz-code/clinv/workflows/Python%20package/badge.svg)](https://github.com/lyz-code/clinv/actions)

# Clinv

`clinv` is a command line inventory for DevSecOps resources in AWS.

# Features

* Manage a dynamic inventory of risk management resources (Projects, Services,
  Information, People) and infrastructure resources (EC2, RDS, S3, Route53, IAM
  users, IAM groups...).
* Add risk management metadata to your AWS resources.
* Monitor if there are resources that are not inside your inventory.
* Perform regular expression searches on all your resources.
* Get all your resources information.
* Works from the command line.

# Install

```bash
pip install clinv
```

`clinv` will use your AWS cli credentials, therefore you must have them
configured.

# Usage

`clinv` will make all the operations on your local inventory. To sync what's
in your AWS account with your local inventory, execute `clinv generate`.

## Generate

`clinv generate` uses `boto3` to update what is in your AWS inventory, right now
it is able to import the following resources from all the regions:

* Autoscaling Groups.
* EC2.
* IAM users and groups.
* RDS.
* Route53.
* S3.
* Security Groups.
* VPCs.

As it's querying all regions, it can take long to fetch all the data. If you
only want to update a resource type, pass it as an argument to generate. For
example, `clinv generate ec2`.

It will automatically mark the EC2 instances as monitored if they have the tag
`monitor` with value `"True"`.

It will automatically mark the EC2 instances as monitored if they have the tag
`monitor` with value `"True"`.

## List

`clinv list resource_type` will show a list of id and names of the selected
resource type.

In the case of services, it will only display the ones that doesn't have a `state
== terminated`.

## Search

`clinv search search_string` will case insensitively match:

* Project names, aliases and descriptions.
* Service names, aliases and descriptions.
* Information names, aliases and descriptions.
* EC2, RDS and Route53 properties (id, name, instance_type, private ips, public ips,
  descriptions, regions and security group ids).
* People names and emails.
* IAM users, groups and it's attached policies.

And will print the matching information.

The search_string can be a regular expression.

## Unassigned

`clinv unassigned resource_type` will show a list of id and names of elements
that are unassigned.

If `resource_type` is `ec2`, `rds`, `s3`, `route53`, it will search for
instances that aren't assigned in a `service`.
If `resource_type` is `people`, `service` or `information`, it will search for instances
that aren't assigned to a `project`.

## Monitor

`clinv monitor monitor_status` will show a list of id and names of elements
that have the specified `monitor_status`. The `monitor_status` can be one of:
`true`, `false` and `unknown`.

## Export

`clinv export` will create an ods file with the inventory in `~/.local/share/clinv/inventory.ods`

# Data Files

All data used by `clinv` is saved into yaml files in the data path directory (by
default `~/.local/share/clinv`).

* *source_data.yaml*: Raw information of the AWS account, generally with
  stripped dictionaries from boto3 resources.
* *user_data.yaml*: Raw clinv additional data explained below.

## The user_data.yaml file

The user_data file contains information of the following types of resources:

* Projects
* Informations
* Services
* AWS resources

`clinv` still doesn't support the creation of resources, therefore I suggest
that you configure your editor to add templates (for example Ultisnip for
neovim).

### Projects

Projects represent the reason for a group of service and information assets to
exist.

An example of a project could be:
```yaml
projects:
  pro-01:
    name: Clinv project
    aliases: Other name for the project
    description: Project to develope clinv
    informations:
    - inf-01
    - inf-02
    links:
      homepage: https://git.digitales.cslabrecha.org/lyz/clinv
      docs: https://git.digitales.cslabrecha.org/lyz/clinv
    people:
    - peo-01
    services:
    - ser-01
    - ser-02
    - ser-03
    state: active
```

### Informations

Represent an information asset.

An example of an information asset could be:
```yaml
informations:
  inf-01:
    name: Clinv source code
    description: Clinv source code
    personal_data: false
    responsible: peo-1
    state: active
```

### Services

Represent a service asset.

An example of a service asset could be:
```yaml
services:
  ser-01:
    name: Clint homepage
    description: Clint homepage
    access: public
    aws:
      ec2:
      - i-xxxxxxxxxxxx
      route53:
      - XXXXXXX-blabla.clinv.org-cname
      rds:
      s3:
      iam_group:
    endpoints:
      - https://www.thispagedoesnot.exist
    responsible: peo-01
    informations:
    - inf-01
    links:
      agile board: tbd
      ci: tbd
      docs:
        deploy: tbd
        internal: tbd
        ops: tbd
        public: tbd
      issues: tbd
      source code: https://git.cloud.icij.org/staff/cassandra-prophecies
    authentication:
      method: sso
      2fa: true
    users:
    - admins
    - partners
    - internet
```

### People

Represent a person.

An example of a service asset could be:
```yaml
people:
  peo-01:
    name: Lyz
    description: Administrator
    state: active
    email: lyz@clinv.org
    iam_user: 'iamuser_lyz'
```

### AWS Resources

Represents AWS resources, we'll show a typical resource template, though
a default one is filled up when `clinv generate` is issued.

#### EC2

```yaml
ec2:
  i-xxxxxxxxxxxxxxxxx:
    description: 'Clinv homepage'
    to_destroy: false
    environment: 'production'
```

#### RDS

```yaml
rds:
  db-xxxxxxxxxxxxxxxxxxxxxxxxxx:
    description: Clinv backend database
    environment: production
    region: eu-east-1
    to_destroy: false
```

#### Route53

```yaml
route53:
  zone_id-clinv.com-cname:
    description: 'Public endpoint to the clinv frontened'
    to_destroy: true
```

#### S3

```yaml
s3:
  clinv-bucket:
    description: Webpage static storage bucket
    desired_permissions:
      read: public
      write: private
    environment: production
    state: active
    to_destroy: false
```

#### IAM Groups

```yaml
iam_groups:
  arn:aws:iam::xxxxxxxxxxxx:group/admin:
    description: AWS administrators.
    desired_users:
    - arn:aws:iam::xxxxxxxxxxxx:user/lyz
    - arn:aws:iam::xxxxxxxxxxxx:user/user_1
    name: Administrator
    state: active
    to_destroy: false
```

#### IAM Users

```yaml
iam_users:
  arn:aws:iam::xxxxxxxxxxxx:user/lyz:
    description: Lyz AWS IAM User
    name: Lyz
    state: active
    to_destroy: false
```

# Contributing

If you want to contribute with the project, first read [the project
guidelines](docs/hacking.md) and then contribute :).

You can also see the roadmap of the project in the [todo](docs/todo.md).

If you want to create a new source or resource go to [this
file](docs/source.md).

If you want to create a new report go to [this file](docs/report.md).

# Test

To run the tests first install `tox`

```bash
pip3 install tox
```

And then run the tests

```bash
tox
```

# Collaborators

This project is being developed with the help of [ICIJ](https://www.icij.org)

# Authors

lyz
