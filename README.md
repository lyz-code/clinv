# Clinv

`clinv` is a command line inventory for devsecops resources in AWS.

# Install

```bash
git clone https://github/jstxu/clinv
cd clinv
virtualenv -p python3 clinv
source clinv/bin/activate
pip3 install -r requirements.txt
python3 setup.py install
mkdir ~/.local/share/clinv
touch ~/.local/share/clinv/raw_data.yaml
```

`clinv` will use your AWS cli credentials, therefore you must have them
configured.

# Usage

`clinv` will make all the operations on your local inventory. To sync what's
in your AWS account with your local inventory, execute `clinv generate`.

## Export

`clinv export` will create an ods file with the inventory in `~/.local/share/clinv/inventory.ods`

## Generate

`clinv generate` uses boto3 to update what is in your AWS inventory, right now
it imports the following resources from all the regions:

* EC2 instances

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
* EC2 and RDS properties (id, name, instance_type, private ips, public ips,
  descriptions, regions and security group ids).

And will print the matching information.

The search_string can be a regular expression.

## Unassigned

`clinv unassigned resource_type` will show a list of id and names of elements
that are unassigned.

If `resource_type` is `ec2`, it will search for instances that aren't assigned
in a `service`.
If `resource_type` is `service` or `information`, it will search for instances
that aren't assigned to a `project`.

# Data Files

All data used by `clinv` is saved into yaml files in the data path directory (by
default `~/.local/share/clinv`).

* *raw_inventory.yaml*: Raw information of the AWS account, generally with
  stripped dictionaries from boto3 resources.
* *raw_data.yaml*: Raw clinv additional data explained below.

## The raw_data.yaml file

The raw_data file contains information of the following types of resources:

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
    description: Project to develope clinv
    informations:
    - inf-01
    - inf-02
    links:
      homepage: https://github.com/jstxu/clinv
      docs: https://github.com/jstxu/clinv
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
    responsible: jstxu
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
    endpoints:
      - https://www.thispagedoesnot.exist
    responsible: jstxu
    informations:
    authentication:
      method: sso
      2fa: true
```

### AWS Resources

Represents AWS resources

#### EC2

Represents an ec2 instance

An example could be:


```yaml
ec2:
  i-xxxxxxxxxxxxxxxxx:
    description: 'Clinv homepage'
    to_destroy: false
    environment: 'production'
```

# Test

To run the tests first install `tox`

```bash
pip3 install tox
```

And then run the tests

```bash
tox
```

# Authors

jstxu
