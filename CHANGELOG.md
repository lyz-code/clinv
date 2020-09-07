## 0.9.0 / 2020-09-07

### Feat

- Allow partial generation of the inventory
- Populate the ec2 monitor attribute with the instance tags

### Fix

- Rename monitored report and attributes to monitor
- Upgrade dependencies

## 0.8.0 / 2020-06-23

### Feat

- Add Autoscaling Group support.

## 0.7.0 / 2020-04-29

### Feat

* Add SecurityGroup support
* Add VPC support
* Search by security group in the EC2
* Check for CIDR, port, and security groups with is_related and search methods
* Test VPC security groups in RDS instances
* Search in EC2 RDS and Securitygroups by VPC
* Add RDS engine information at print
* Print security groups in RDS information
* Added service dependencies to services
* Created Active report
* Created Unused report

### Fix

* Refactor code to prune_dictionary abstract class method
* Added _match_dict method to ClinvGenericResource and Improved EC2 security group print support.
* Added region to the EC2 print report
* Improved security groups search on RDS


## 0.6.2 / 2020-04-06

* Deprecate python 3.5
* Updated requirements
* Small fixes on the monitored repo
* Add first version of the MonitoredReport
* Unassigned reports don't show terminated resources

## 0.6.1 / 2019-11-27

* Added RDS database endpoint to print

## 0.6.0 / 2019-11-25

* Allow search on service aws resources

## 0.5.1 / 2019-11-19

* Fixed IAM Group Policies fetching
* Added github actions
* Changed git url
* Updated README

## 0.5.0 / 2019-11-12

* Added IAM User source and resource
* Added People source and resource
* Added IAM Group source and resources
* Added regular expression match on ec2 search ips
* Added to_destroy property to ClinvGenericResource

## 0.4.0 / 2019-08-28

* Added S3 support

## 0.3.0 / 2019-08-27

* Refactor RiskManagementsrc to Projectsrc, Servicesrc and Informationsrc
* Refactored search report
* Refactored export and unassigned reports
* Refactored EC2 to EC2src
* Refactored RDS and RiskManagement to it's own sources
* Refactored clinv generate and load to inventory
* WIP: Decoupled Route53src fetch and generate data
* WIP: Refactor Clinv object into Inventory
* Fixed bug in Route53 refactor
* Refactored Route53 source into the sources package
* Updated dependencies
* Added more information to the service print method
* Added print method for the active resources
* Added to_destroy property to Route53 resource
* Typo on readme

## 0.2.0 / 2019-07-18

* Added Route53 support
* Added print method for the resources
* Added docstrings
* Add rds to the list report
* Added export of services and informations

## 0.1.0 / 2019-07-10

* Refactor _get_resource_names Add exported_project_data to the ods
* Add docstrings to resources.py Add project export
* Create _export_to_rds
* Refactor resource print to short_print
* Refactor _export to _export_ec2
* Create the unassigned all report
* Refactor ClinvAWSResourceTests and ClinvAWSResource
* Update readme
* Refactor _update_inventory
* WIP: Add rds support
* Refactor projects, services and informations to their own objects
* Fetch ec2 resources from all regions
* Add ec2 object region property
* Add regions property to clinv
* Add export command
* Refactor the list and print of resources
* Update Readme
* Update requirements
* Refactor update_inventory
* Add export subcommand in cli and init
* Refactor parser and clinv mocks in test_cli
* Search in description and aliases
* Refactor search in ec2 class
* Add stop reason when displaying instance information
* Added list subcommand
* Added project, information and service search
* Added readme
* Add regular expression search
* Add unassigned ec2, services, informations
* Shorten the ec2 saved raw inventory
* Refactor EC2Instance
* Add ec2.type
* Initial iteration
* Added Gitignore
