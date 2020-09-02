"""
Module to store the AWS sources used by Clinv.

Classes:
    AWSBasesrc: Class to gather the common methods for the AWS sources.
    ASGsrc: Class to gather and manipulate the AWS ASG sources.
    EC2src: Class to gather and manipulate the AWS EC2 sources.
    IAMGroupsrc: Class to gather and manipulate the AWS IAM Groups sources.
    IAMUsersrc: Class to gather and manipulate the AWS IAM Users sources.
    RDSsrc: Class to gather and manipulate the AWS RDS sources.
    Route53src: Class to gather and manipulate the AWS Route53 sources.
    S3src: Class to gather and manipulate the AWS S3 sources.
    SecurityGroupsrc: Class to gather and manipulate the AWS Security Groups
        sources.
    VPCsrc: Class to gather and manipulate the AWS VPC sources.

    ClinvAWSResource: Abstract class to extend ClinvGenericResource, it gathers
        common method and attributes for the AWS resources.
    EC2: Abstract class to extend ClinvAWSResource, it gathers method and
        attributes for the ASG resources.
    EC2: Abstract class to extend ClinvAWSResource, it gathers method and
        attributes for the EC2 resources.
    IAMGroup: Abstract class to extend ClinvGenericResource, it gathers method
        and attributes for the IAM Group resources.
    IAMUser: Abstract class to extend ClinvGenericResource, it gathers method
        and attributes for the IAM User resources.
    RDS: Abstract class to extend ClinvAWSResource, it gathers method and
        attributes for the RDS resources.
    Route53: Abstract class to extend ClinvGenericResource, it gathers method
        and attributes for the Route53 resources.
    S3: Abstract class to extend ClinvGenericResource, it gathers method
        and attributes for the S3 resources.
    SecurityGroup: Abstract class to extend ClinvGenericResource, it gathers
        method and attributes for the SecurityGroup resources.
    VPC: Abstract class to extend ClinvGenericResource, it gathers method
        and attributes for the VPC resources.
"""

import re

import boto3
from clinv.sources import ClinvGenericResource, ClinvSourcesrc
from tabulate import tabulate


class AWSBasesrc(ClinvSourcesrc):
    """
    Class to gather the common methods for the AWS sources.

    Public properties:
        regions (list): List of the AWS regions.

    Public attributes:
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)

    @property
    def regions(self):
        """
        Do aggregation of the AWS regions to generate the self.regions list.

        Returns:
            list: AWS Regions.
        """
        ec2 = boto3.client("ec2")
        return [region["RegionName"] for region in ec2.describe_regions()["Regions"]]


class ASGsrc(AWSBasesrc):
    """
    Class to gather and manipulate the ASG resources.

    Parameters:
        source_data (dict): ASGsrc compatible source_data
        dictionary.
        user_data (dict): ASGsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "asg"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching ASG inventory")
        raw_data = {}

        for region in self.regions:
            ec2 = boto3.client("autoscaling", region_name=region)
            raw_data[region] = ec2.describe_auto_scaling_groups()["AutoScalingGroups"]

        prune_keys = [
            "DefaultCooldown",
            "EnabledMetrics",
            "NewInstancesProtectedFromScaleIn",
            "SuspendedProcesses",
            "Tags",
            "TerminationPolicies",
        ]

        for region in raw_data.keys():
            for resource in raw_data[region]:
                asg_id = "asg-{}".format(resource["AutoScalingGroupName"])
                resource["region"] = region
                resource = self.prune_dictionary(resource, prune_keys)
                self.source_data[asg_id] = resource

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "state": "tbd",
                    "to_destroy": "tbd",
                    "description": "tbd",
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with ASG resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: ASG inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = ASG({resource_id: resource})

        return inventory


class EC2src(AWSBasesrc):
    """
    Class to gather and manipulate the EC2 resources.

    Parameters:
        source_data (dict): EC2src compatible source_data
        dictionary.
        user_data (dict): EC2src compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "ec2"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
        {
            'us-east-1': [
                {
                    'Groups': [],
                    'Instances': [
                        {
                            'ImageId': 'ami-ffcsssss',
                            'InstanceId': 'i-023desldk394995ss',
                            'InstanceType': 'c4.4xlarge',
                            'LaunchTime': datetime.datetime(
                                2018, 5, 10, 7, 13, 17, tzinfo=tzutc()
                            ),
                            'NetworkInterfaces': [
                                {
                                    'PrivateIpAddresses': [
                                        {
                                            'Association': {
                                                'IpOwnerId': '585394460090',
                                                'PublicDnsName': 'ec2.com',
                                                'PublicIp': '32.312.444.22'
                                            },
                                            'Primary': True,
                                            'PrivateDnsName': 'ec2.nternal',
                                            'PrivateIpAddress': '1.1.1.1',
                                        }
                                    ],
                                }
                            ],
                            'SecurityGroups': [
                                {
                                    'GroupId': 'sg-f2234gf6',
                                    'GroupName': 'sg-1'
                                },
                                {
                                    'GroupId': 'sg-cwfccs17',
                                    'GroupName': 'sg-2'
                                }
                            ],
                            'State': {'Code': 16, 'Name': 'running'},
                            'StateTransitionReason': '',
                            'Tags': [{'Key': 'Name', 'Value': 'name'}],
                            'VpcId': 'vpc-31084921'
                        }
                    ],
                    'OwnerId': '585394460090',
                    'ReservationId': 'r-039ed99cad2bb3da5'
                },
            ],
        }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching EC2 inventory")
        self.source_data = {}

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region)
            self.source_data[region] = ec2.describe_instances()["Reservations"]

        prune_keys = [
            "AmiLaunchIndex",
            "Architecture",
            "BlockDeviceMappings",
            "CapacityReservationSpecification",
            "ClientToken",
            "CpuOptions",
            "EbsOptimized",
            "HibernationOptions",
            "Hypervisor",
            "KeyName",
            "Monitoring",
            "Placement",
            "PrivateDnsName",
            "PrivateIpAddress",
            "ProductCodes",
            "PublicDnsName",
            "PublicIpAddress",
            "RootDeviceName",
            "RootDeviceType",
            "SourceDestCheck",
            "SubnetId",
            "VirtualizationType",
        ]
        network_prune_keys = [
            "Association",
            "Attachment",
            "Description",
            "Groups",
            "InterfaceType",
            "Ipv6Addresses",
            "MacAddress",
            "NetworkInterfaceId",
            "OwnerId",
            "PrivateDnsName",
            "PrivateIpAddress",
            "SourceDestCheck",
            "Status",
            "SubnetId",
            "VpcId",
        ]

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                for instance in resource["Instances"]:
                    instance = self.prune_dictionary(instance, prune_keys)
                    for interface in instance["NetworkInterfaces"]:
                        interface = self.prune_dictionary(interface, network_prune_keys)
        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                for instance in resource["Instances"]:
                    instance_id = instance["InstanceId"]
                    try:
                        self.user_data[instance_id]
                    except KeyError:
                        self.user_data[instance_id] = {
                            "description": "",
                            "to_destroy": "tbd",
                            "environment": "tbd",
                            "monitor": "tbd",
                            "region": region,
                        }

                    for tag in instance["Tags"]:
                        if tag["Key"] == "monitor" and tag["Value"] == "True":
                            self.user_data[instance_id]["monitor"] = True

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with EC2 resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: EC2 inventory with user and source data
        """

        inventory = {}
        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                for instance in resource["Instances"]:
                    instance_id = instance["InstanceId"]

                    for key, value in self.user_data[instance_id].items():
                        instance[key] = value

                    inventory[instance_id] = EC2({instance_id: instance})
        return inventory


class IAMGroupsrc(AWSBasesrc):
    """
    Class to gather and manipulate the IAMGroup resources.

    Parameters:
        source_data (dict): IAMGroupsrc compatible source_data
        dictionary.
        user_data (dict): IAMGroupsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "iam_groups"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching IAMGroup inventory")
        self.source_data = {}

        iam = boto3.client("iam")
        iam_group_names = [group["GroupName"] for group in iam.list_groups()["Groups"]]

        for group_name in iam_group_names:
            group_data = iam.get_group(GroupName=group_name)
            group_id = group_data["Group"]["Arn"]
            self.source_data[group_id] = group_data["Group"]
            self.source_data[group_id].pop("Arn")
            self.source_data[group_id]["Users"] = [
                user["Arn"] for user in group_data["Users"]
            ]
            self.source_data[group_id]["InlinePolicies"] = [
                policy
                for policy in iam.list_group_policies(GroupName=group_name)[
                    "PolicyNames"
                ]
            ]
            self.source_data[group_id]["AttachedPolicies"] = [
                policy["PolicyArn"]
                for policy in iam.list_attached_group_policies(GroupName=group_name)[
                    "AttachedPolicies"
                ]
            ]

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            # Define the default user_data of the record
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "name": resource["GroupName"],
                    "description": "tbd",
                    "to_destroy": "tbd",
                    "state": "tbd",
                    "desired_users": resource["Users"],
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with IAMGroup resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: IAMGroup inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = IAMGroup({resource_id: resource})

        return inventory


class IAMUsersrc(AWSBasesrc):
    """
    Class to gather and manipulate the IAM User resources.

    Parameters:
        source_data (dict): IAMUsersrc compatible source_data
        dictionary.
        user_data (dict): IAMUsersrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "iam_users"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
                'arn:aws:iam::XXXXXXXXXXXX:user/user_1': {
                    'UserName': 'User 1'
                    'Path': '/',
                    'CreateDate': datetime.datetime(
                        2019, 2, 7, 12, 15, 57, tzinfo=tzutc()
                    ),
                    'UserId': 'XXXXXXXXXXXXXXXXXXXXX',
                },
                'arn:aws:iam::XXXXXXXXXXXX:user/user_2': {
                    'UserName': 'User 2'
                    'Path': '/',
                    'CreateDate': datetime.datetime(
                        2019, 2, 7, 12, 15, 57, tzinfo=tzutc()
                    ),
                    'UserId': 'XXXXXXXXXXXXXXXXXXXXX',
                },
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching IAM users inventory")
        self.source_data = {}

        iam = boto3.client("iam")
        iam_users = iam.list_users()["Users"]

        for record in iam_users:
            user_id = record["Arn"]
            record.pop("Arn")
            try:
                record.pop("PasswordLastUsed")
            except KeyError:
                pass
            self.source_data[user_id] = record

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            # Define the default user_data of the record
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "name": resource["UserName"],
                    "description": "tbd",
                    "to_destroy": "tbd",
                    "state": "tbd",
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with IAM resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: IAM inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = IAMUser({resource_id: resource})

        return inventory


class RDSsrc(AWSBasesrc):
    """
    Class to gather and manipulate the AWS RDS resources.

    Parameters:
        source_data (dict): RDSsrc compatible source_data
        dictionary.
        user_data (dict): RDSsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "rds"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            'us-east-1': [
                {
                    'AllocatedStorage': 100,
                    'AssociatedRoles': [],
                    'AutoMinorVersionUpgrade': True,
                    'AvailabilityZone': 'us-east-1a',
                    'BackupRetentionPeriod': 7,
                    'CACertificateIdentifier': 'rds-ca-2015',
                    'DBInstanceArn': 'arn:aws:rds:us-east-1:224119285:db:db',
                    'DBInstanceClass': 'db.t2.micro',
                    'DBInstanceIdentifier': 'rds-name',
                    'DBInstanceStatus': 'available',
                    'DBSecurityGroups': [],
                    'DBSubnetGroup': {
                        'DBSubnetGroupDescription': 'Created from the RDS '
                        'Management Console',
                        'DBSubnetGroupName': 'default-vpc-v2dcp2jh',
                        'SubnetGroupStatus': 'Complete',
                        'Subnets': [
                            {
                                'SubnetAvailabilityZone': {
                                    'Name': 'us-east-1a'
                                },
                                'SubnetIdentifier': 'subnet-42sfl222',
                                'SubnetStatus': 'Active'
                            },
                            {
                                'SubnetAvailabilityZone': {
                                    'Name': 'us-east-1e'
                                },
                                'SubnetIdentifier': 'subnet-42sfl221',
                                'SubnetStatus': 'Active'
                            },
                        ],
                        'VpcId': 'vpc-v2dcp2jh'},
                    'DbiResourceId': 'db-YDFL2',
                    'DeletionProtection': True,
                    'Endpoint': {
                        'Address': 'rds-name.us-east-1.rds.amazonaws.com',
                        'HostedZoneId': '202FGHSL2JKCFW',
                        'Port': 5521
                    },
                    'Engine': 'mariadb',
                    'EngineVersion': '1.2',
                    'InstanceCreateTime': datetime.datetime(
                        2019, 6, 17, 15, 15, 8, 461000, tzinfo=tzutc()
                    ),
                    'Iops': 1000,
                    'MasterUsername': 'root',
                    'MultiAZ': True,
                    'PreferredBackupWindow': '03:00-04:00',
                    'PreferredMaintenanceWindow': 'fri:04:00-fri:05:00',
                    'PubliclyAccessible': False,
                    'StorageEncrypted': True,
                },
            ],
        }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching RDS inventory")
        self.source_data = {}

        for region in self.regions:
            rds = boto3.client("rds", region_name=region)
            self.source_data[region] = rds.describe_db_instances()["DBInstances"]

        prune_keys = [
            "CopyTagsToSnapshot",
            "DBParameterGroups",
            "DbInstancePort",
            "DomainMemberships",
            "EnhancedMonitoringResourceArn",
            "IAMDatabaseAuthenticationEnabled",
            "LatestRestorableTime",
            "LicenseModel",
            "MonitoringInterval",
            "MonitoringRoleArn",
            "OptionGroupMemberships",
            "PendingModifiedValues",
            "PerformanceInsightsEnabled",
            "PerformanceInsightsKMSKeyId",
            "PerformanceInsightsRetentionPeriod",
            "ReadReplicaDBInstanceIdentifiers",
            "StorageType",
        ]

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                resource = self.prune_dictionary(resource, prune_keys)

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                resource_id = resource["DbiResourceId"]
                # Define the default user_data of the resource
                try:
                    self.user_data[resource_id]
                except KeyError:
                    self.user_data[resource_id] = {
                        "description": "",
                        "to_destroy": "tbd",
                        "environment": "tbd",
                        "monitor": "tbd",
                        "region": region,
                    }
        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with RDS resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: RDS inventory with user and source data
        """

        inventory = {}

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                resource_id = resource["DbiResourceId"]

                for key, value in self.user_data[resource_id].items():
                    resource[key] = value

                inventory[resource_id] = RDS({resource_id: resource})

        return inventory


class Route53src(AWSBasesrc):
    """
    Class to gather and manipulate the AWS Route53 resources.

    Parameters:
        source_data (dict): Route53src compatible source_data dictionary.
        user_data (dict): Route53src compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "route53"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
                'hosted_zones': [
                    {
                        'Config': {
                            'Comment': 'This is the description',
                            'PrivateZone': False,
                        },
                        'Id': '/hostedzone/hosted_zone_id',
                        'Name': 'hostedzone.org',
                        'ResourceRecordSetCount': 1,
                        'records': [
                            {
                                'Name': 'record1.clinv.org',
                                'ResourceRecords': [
                                    {
                                        'Value': '127.0.0.1'
                                    },
                                    {
                                        'Value': 'localhost'
                                    },
                                ],
                                'TTL': 172800,
                                'Type': 'CNAME'
                            },
                        ],
                    },
                ],
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching Route53 inventory")
        self.source_data = {}

        route53 = boto3.client("route53")

        # Fetch the hosted zones
        self.source_data["hosted_zones"] = route53.list_hosted_zones()["HostedZones"]

        # Prune unneeded information
        prune_keys = ["CallerReference"]
        for zone in self.source_data["hosted_zones"]:
            zone = self.prune_dictionary(zone, prune_keys)

        # Fetch the records
        for zone in self.source_data["hosted_zones"]:
            raw_records = route53.list_resource_record_sets(HostedZoneId=zone["Id"],)

            zone["records"] = raw_records["ResourceRecordSets"]

            while raw_records["IsTruncated"]:
                raw_records = route53.list_resource_record_sets(
                    HostedZoneId=zone["Id"],
                    StartRecordName=raw_records["NextRecordName"],
                    StartRecordType=raw_records["NextRecordType"],
                )
                for record in raw_records["ResourceRecordSets"]:
                    zone["records"].append(record)

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for zone in self.source_data["hosted_zones"]:
            for record in zone["records"]:
                record_id = "{}-{}-{}".format(
                    re.sub(r"/hostedzone/", "", zone["Id"]),
                    re.sub(r"\.$", "", record["Name"]),
                    record["Type"].lower(),
                )

                # Define the default user_data of the record
                try:
                    self.user_data[record_id]
                except KeyError:
                    self.user_data[record_id] = {
                        "description": "tbd",
                        "to_destroy": "tbd",
                        "monitor": "tbd",
                        "state": "active",
                    }
        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with Route53 resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: Route53 inventory with user and source data
        """

        inventory = {}

        for zone in self.source_data["hosted_zones"]:
            for record in zone["records"]:
                record_id = "{}-{}-{}".format(
                    re.sub(r"/hostedzone/", "", zone["Id"]),
                    re.sub(r"\.$", "", record["Name"]),
                    record["Type"].lower(),
                )

                # Load the user_data into the source_data record
                for key, value in self.user_data[record_id].items():
                    record[key] = value

                # Add clinv needed information
                record["hosted_zone"] = {
                    "id": zone["Id"],
                    "name": zone["Name"],
                    "private": zone["Config"]["PrivateZone"],
                }

                inventory[record_id] = Route53({record_id: record})
        return inventory


class S3src(AWSBasesrc):
    """
    Class to gather and manipulate the S3 resources.

    Parameters:
        source_data (dict): S3src compatible source_data
        dictionary.
        user_data (dict): S3src compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "s3"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
                's3_bucket_name': {
                    'CreationDate': datetime.datetime(
                        2012, 12, 12, 0, 7, 46, tzinfo=tzutc()
                    ),
                    'Name': 's3_bucket_name',
                    'permissions': {
                        'read': 'public',
                        'write': 'private',
                    },
                    'Grants': [
                        {
                            'Grantee': {
                                'DisplayName': 'admin',
                                'ID': 'admin_id',
                                'Type': 'CanonicalUser'
                            },
                            'Permission': 'READ'
                        },
                        {
                            'Grantee': {
                                'DisplayName': 'admin',
                                'ID': 'admin_id',
                                'Type': 'CanonicalUser'
                            },
                            'Permission': 'WRITE'
                        },
                        {
                            'Grantee': {
                                'Type': 'Group',
                                'URI': 'http://acs.amazonaws.com/'
                                        'groups/global/AllUsers'
                            },
                            'Permission': 'READ'
                        },
                    ],
                },
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching S3 inventory")
        self.source_data = {}

        public_acl_indicator = "http://acs.amazonaws.com/groups/global/AllUsers"
        permissions_to_check = ["READ", "WRITE"]

        # Create S3 client, describe buckets.
        s3 = boto3.client("s3")
        list_bucket_response = s3.list_buckets()

        for bucket_dictionary in list_bucket_response["Buckets"]:
            bucket_dictionary["Grants"] = s3.get_bucket_acl(
                Bucket=bucket_dictionary["Name"]
            )["Grants"]
            bucket_dictionary["permissions"] = {}

            # Check if there is any public access to the bucket
            for grant in bucket_dictionary["Grants"]:
                for (key, value) in grant.items():
                    if key == "Permission" and any(
                        permission in value for permission in permissions_to_check
                    ):
                        for (grantee_attribute_key, grantee_attribute_value) in grant[
                            "Grantee"
                        ].items():
                            if (
                                "URI" in grantee_attribute_key
                                and grant["Grantee"]["URI"] == public_acl_indicator
                            ):
                                bucket_dictionary["permissions"][value] = "public"

            # If there is no public access, it means it's private
            for permission in permissions_to_check:
                try:
                    bucket_dictionary["permissions"][permission]
                except KeyError:
                    bucket_dictionary["permissions"][permission] = "private"

            self.source_data[bucket_dictionary["Name"]] = bucket_dictionary
        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            # Define the default user_data of the record
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "description": "",
                    "to_destroy": "tbd",
                    "environment": "tbd",
                    "desired_permissions": {"read": "tbd", "write": "tbd"},
                    "state": "active",
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with S3 resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: S3 inventory with user and source data
        """

        inventory = {}
        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = S3({resource_id: resource})

        return inventory


class SecurityGroupsrc(AWSBasesrc):
    """
    Class to gather and manipulate the SecurityGroup resources.

    Parameters:
        source_data (dict): SecurityGroupsrc compatible source_data
        dictionary.
        user_data (dict): SecurityGroupsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "security_groups"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
                'sg-xxxxxxxx': {
                    'description': 'default group',
                    'GroupName': 'default',
                    'region': 'us-east-1',
                    'IpPermissions': [
                        {
                            'FromPort': 0,
                            'IpProtocol': 'udp',
                            'IpRanges': [],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': 65535,
                            'UserIdGroupPairs': [],
                        },
                        ...
                    ],
                    'IpPermissionsEgress': [],
                },
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching SecurityGroup inventory")
        self.source_data = {}
        raw_data = {}

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region)
            raw_data[region] = ec2.describe_security_groups()["SecurityGroups"]

        prune_keys = [
            "GroupId",
            "OwnerId",
            "Description",
        ]

        for region in raw_data.keys():
            for resource in raw_data[region]:
                security_group_id = resource["GroupId"]
                resource["description"] = resource["Description"]
                resource["region"] = region
                resource = self.prune_dictionary(resource, prune_keys)
                self.source_data[security_group_id] = resource

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "state": "tbd",
                    "to_destroy": "tbd",
                    "ingress": resource["IpPermissions"],
                    "egress": resource["IpPermissionsEgress"],
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with SecurityGroup resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: SecurityGroup inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = SecurityGroup({resource_id: resource})

        return inventory


class VPCsrc(AWSBasesrc):
    """
    Class to gather and manipulate the VPC resources.

    Parameters:
        source_data (dict): VPCsrc compatible source_data
        dictionary.
        user_data (dict): VPCsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = "vpc"

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info("Fetching VPC inventory")
        raw_data = {}

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region)
            raw_data[region] = ec2.describe_vpcs()["Vpcs"]

        prune_keys = [
            "CidrBlockAssociationSet",
            "OwnerId",
            "VpcId",
        ]

        for region in raw_data.keys():
            for resource in raw_data[region]:
                vpc_id = resource["VpcId"]
                resource["region"] = region
                resource = self.prune_dictionary(resource, prune_keys)
                self.source_data[vpc_id] = resource

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        for resource_id, resource in self.source_data.items():
            try:
                self.user_data[resource_id]
            except KeyError:
                self.user_data[resource_id] = {
                    "state": "tbd",
                    "to_destroy": "tbd",
                    "description": "tbd",
                }

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with VPC resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: VPC inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = VPC({resource_id: resource})

        return inventory


class ClinvAWSResource(ClinvGenericResource):
    """
    Abstract class to extend ClinvGenericResource, it gathers common method and
    attributes for the AWS resources.

    Public methods:
        search: Search in the resource data if a string matches.

    Public properties:
        monitor: Returns if the resource is monitor.
        region: Returns the region of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def region(self):
        """
        Do aggregation of data to return the region of the resource.

        Returns:
            str: Region of the resource.
        """

        return self._get_field("region", "str")

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            security groups
            region
            resource size


        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by region
        if re.match(search_string, self.region):
            return True

        # Search by type
        if re.match(search_string, self.type):
            return True

        return False

    @property
    def monitor(self):
        """
        Do aggregation of data to return if the resource is being monitor.

        Returns:
            str: Resource type.
        """

        try:
            monitor = self._get_field("monitor", "str")
            if monitor not in [True, False]:
                monitor = "unknown"
        except KeyError:
            monitor = "unknown"

        return monitor


class ASG(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the ASG resources.

    Public methods:
        print: Prints information of the resource.
        print_instances: Prints information of the resource.

    Public properties:
        name: Returns the name of the record.
        instances: Return information of the autoscaling instances.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def instances(self):
        """
        Gather information to show the autoscaling instances information. With
        the following structure:
            {
                'ec2-id':{
                    'AvailabilityZone': 'eu-east-1a',
                    'HealthStatus': 'Healthy',
                    'LaunchConfigurationName': 'lc_name',
                    'LifecycleState': 'InService',
                    'ProtectedFromScaleIn': False
                }
            }
        Returns:
            dict: Instances information
        """

        instances = {}

        for instance in self._get_field("Instances"):
            instance = instance.copy()
            id = instance["InstanceId"]
            instance.pop("InstanceId")
            instances[id] = instance
        return instances

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("AutoScalingGroupName")

    def print_instances(self):
        """
        Print instances information
        """
        headers = [
            "Instance",
            "Status",
            "Zones",
            "LaunchConfiguration",
        ]
        instances_data = []

        for instance in self._get_field("Instances"):
            instances_data.append(
                [
                    instance["InstanceId"],
                    "{}/{}".format(
                        instance["HealthStatus"], instance["LifecycleState"],
                    ),
                    instance["AvailabilityZone"],
                    instance["LaunchConfigurationName"][:35],
                ]
            )

        print(tabulate(instances_data, headers=headers, tablefmt="simple"))

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy)),
        print("  Zones: {}".format(", ".join(self._get_field("AvailabilityZones"))))
        print(
            "  Launch Configuration: {}".format(
                self._get_field("LaunchConfigurationName")
            )
        )
        print("  Healthcheck: {}".format(self._get_field("HealthCheckType")))
        print("  Capacity: {}".format(len(self._get_field("Instances"))))
        print("    Desired: {}".format(self._get_field("DesiredCapacity")))
        print("    Max: {}".format(self._get_field("MaxSize")))
        print("    Min: {}".format(self._get_field("MinSize")))
        self.print_instances()


class EC2(ClinvAWSResource):
    """
    Class to extend the ClinvAWSResource abstract class. It gathers methods and
    attributes for the EC2 resources.

    Public methods:
        search: Search in the resource data if a string matches.
        print: Prints information of the resource.

    Public properties:
        name: Returns the name of the resource.
        security_groups: Returns the security groups of the resource.
        private_ips: Returns the private ips of the resource.
        public_ips: Returns the public ips of the resource.
        state: Returns the state of the resource.
        type: Returns the type of the resource.
        state_transition: Returns the reason of the transition of the resource.
        vpc: Returns the VPC of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        try:
            for tag in self.raw["Tags"]:
                if tag["Key"] == "Name":
                    return tag["Value"]
        except KeyError:
            pass
        except TypeError:
            pass
        return "none"

    @property
    def security_groups(self):
        """
        Do aggregation of data to return the security groups of the resource.

        Returns:
            dict: Security groups of the resource.
        """

        try:
            return {
                security_group["GroupId"]: security_group["GroupName"]
                for security_group in self.raw["SecurityGroups"]
            }
        except KeyError:
            pass

    @property
    def private_ips(self):
        """
        Do aggregation of data to return the private ips of the resource.

        Returns:
            list: Private ips of the resource.
        """

        private_ips = []
        try:
            for interface in self.raw["NetworkInterfaces"]:
                for address in interface["PrivateIpAddresses"]:
                    private_ips.append(address["PrivateIpAddress"])
        except KeyError:
            pass
        return private_ips

    @property
    def public_ips(self):
        """
        Do aggregation of data to return the public ips of the resource.

        Returns:
            list: Private ips of the resource.
        """

        public_ips = []
        try:
            for interface in self.raw["NetworkInterfaces"]:
                for association in interface["PrivateIpAddresses"]:
                    public_ips.append(association["Association"]["PublicIp"])
        except KeyError:
            pass
        return public_ips

    @property
    def state(self):
        """
        Overrides the parent method to do aggregation of data to return the
        state of the resource.

        Returns:
            str: State of the resource.
        """

        try:
            return self.raw["State"]["Name"]
        except KeyError:
            pass

    @property
    def type(self):
        """
        Do aggregation of data to return the resource type.

        Returns:
            str: Resource type.
        """

        return self._get_field("InstanceType", "str")

    @property
    def state_transition(self):
        """
        Do aggregation of data to return the reason of the state transition of
        the resource.

        Returns:
            str: State transition of the resource.
        """
        return self._get_field("StateTransitionReason", "str")

    @property
    def vpc(self):
        """
        Do aggregation of data to return the resource vpc.

        Returns:
            str: Resource type.
        """

        return self._get_optional_field("VpcId", "str")

    def print(self):
        """
        Do aggregation of data to print information of the resource.

        It's more verbose than short_print but less than describe.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  State: {}".format(self.state))
        if self.state != "running":
            print("  State Reason: {}".format(self.state_transition))
        print("  Type: {}".format(self.type))

        print("  SecurityGroups: ")
        for sg_id, sg_name in self.security_groups.items():
            print("    - {}: {}".format(sg_id, sg_name))

        print("  PrivateIP: {}".format(self.private_ips))
        print("  PublicIP: {}".format(self.public_ips))
        print("  Region: {}".format(self.region))

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            Public Ips
            Private Ips

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvAWSResource searches
        if super().search(search_string):
            return True

        # Search by public IP
        if self._match_list(search_string, self.public_ips):
            return True

        # Search by private IP
        if self._match_list(search_string, self.private_ips):
            return True

        # Search by security group
        if self._match_dict(search_string, self.security_groups):
            return True

        # Search by VPC.
        if self.vpc is not None and re.match(search_string, self.vpc):
            return True

        return False

    @property
    def monitor(self):
        """
        Do aggregation of data to return if the resource is being monitor.

        Returns:
            str: Resource type.
        """

        try:
            monitor = self._get_field("monitor", "str")
            if monitor not in [True, False]:
                monitor = "unknown"
        except KeyError:
            monitor = "unknown"

        return monitor


class IAMGroup(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the IAMGroup resources.

    Public methods:
        print: Prints information of the resource.

    Public properties:
        name: Returns the name of the record.
        users: Return the real users of the group.
        desired_users: Return the desired users of the group.
        inline_policies: Return the inline policies of the group.
        attached_policies: Return the attached policies of the group.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("GroupName", "str")

    @property
    def users(self):
        """
        Do aggregation of data to return the real users of the group.

        Returns:
            list: List of user ids.
        """

        return self._get_field("Users", "list")

    @property
    def desired_users(self):
        """
        Do aggregation of data to return the desired users of the group.

        Returns:
            list: List of user ids.
        """

        return self._get_field("desired_users", "list")

    @property
    def inline_policies(self):
        """
        Do aggregation of data to return the inline policies of the group.

        Returns:
            list: List of policy ids.
        """

        return self._get_field("InlinePolicies", "list")

    @property
    def attached_policies(self):
        """
        Do aggregation of data to return the attached policies of the group.

        Returns:
            list: List of policy ids.
        """

        return self._get_field("AttachedPolicies", "list")

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  Users:"),
        for user_id in self.users:
            print("    - {}".format(user_id))
        print("  AttachedPolicies:"),
        for policy_id in self.attached_policies:
            print("    - {}".format(policy_id))
        print("  InlinePolicies:"),
        for policy_id in self.inline_policies:
            print("    - {}".format(policy_id))
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy)),

    def search(self, search_string):
        """
        Extend the parent search method to include iam group specific search.

        Extend to search by:
            users in group
            Policies ids

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvAWSResource searches
        if super().search(search_string):
            return True

        # Search by user ids
        if self._match_list(search_string, self.users) or self._match_list(
            search_string, self.desired_users
        ):
            return True

        # Search by policy ids
        if self._match_list(search_string, self.attached_policies) or self._match_list(
            search_string, self.inline_policies
        ):
            return True

        return False


class IAMUser(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the IAMUser resources.

    Public properties:
        name: Returns the name of the user.

    Public methods:
        print: Prints information of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy)),


class RDS(ClinvAWSResource):
    """
    Class to extend the ClinvAWSResource abstract class. It gathers methods
    and attributes for the RDS resources.

    Public properties:
        endpoint: Return the database endpoint.
        engine: Return the database type and version.
        name: Returns the name of the resource.
        security_groups: Returns the security groups of the resource.
        type: Returns the type of the resource.
        state: Returns the state of the resource.
        vpc: Returns the VPC of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def engine(self):
        """
        Overrides the parent method to do aggregation of data to return the
        type and version of the resource database.

        Returns:
            str: Name of the resource.
        """

        return "{} {}".format(
            self._get_field("Engine", "str"), self._get_field("EngineVersion", "str"),
        )

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("DBInstanceIdentifier", "str")

    @property
    def state(self):
        """
        Overrides the parent method to do aggregation of data to return the
        state of the resource.

        Returns:
            str: State of the resource.
        """

        return self._get_field("DBInstanceStatus", "str")

    @property
    def security_groups(self):
        """
        Do aggregation of data to return the security groups of the resource.

        Returns:
            list: Security groups of the resource.
        """

        security_groups = self._get_field("DBSecurityGroups", "list")

        for security_group in self._get_field("VpcSecurityGroups", "list"):
            security_groups.append(security_group["VpcSecurityGroupId"])

        return security_groups

    @property
    def type(self):
        """
        Do aggregation of data to return the resource type.

        Returns:
            str: Resource type.
        """

        return self._get_field("DBInstanceClass", "str")

    @property
    def endpoint(self):
        """
        Do aggregation of data to return the resource endpoint.

        Returns:
            str: Resource type.
        """

        endpoint_dict = self._get_field("Endpoint", "dict")
        return "{}:{}".format(endpoint_dict["Address"], endpoint_dict["Port"])

    @property
    def vpc(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self.raw["DBSubnetGroup"]["VpcId"]

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Endpoint: {}".format(self.endpoint)),
        print("  Type: {}".format(self.type))
        print("  Engine: {}".format(self.engine))
        print("  Description: {}".format(self.description))
        print("  SecurityGroups:")
        for security_group in self.security_groups:
            print("    - {}".format(security_group))

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            Security groups
            VPC

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvAWSResource searches
        if super().search(search_string):
            return True

        # Search by security group
        if self._match_list(search_string, self.security_groups):
            return True

        # Search by VPC.
        if re.match(search_string, self.vpc):
            return True

        return False


class Route53(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the Route53 resources.

    Public properties:
        name: Returns the name of the record.
        value: Returns the value of the record.
        type: Returns the type of the record.
        hosted_zone: Returns the hosted zone name of the resource.
        hosted_zone_id: Returns the hosted zone id of the resource.
        monitor: Returns if the resource is being monitor.
        private: Returns if the resource is private.
        print: Prints information of the resource.
        short_print: Prints the resource id.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("Name", "str")

    @property
    def to_destroy(self):
        """
        Overrides the parent method to do aggregation of data to return the
        if we want to destroy the resource.

        Returns:
            str: If we want to destroy the resource
        """

        return self._get_field("to_destroy", "str")

    @property
    def value(self):
        """
        Do aggregation of data to return the value of the record.

        Returns:
            list: Value of the record set
        """

        try:
            return [record["Value"] for record in self.raw["ResourceRecords"]]
        except KeyError:
            return [self.raw["AliasTarget"]["DNSName"]]

    @property
    def type(self):
        """
        Do aggregation of data to return the resource type.

        Returns:
            str: Resource type.
        """

        return self._get_field("Type", "str")

    @property
    def hosted_zone(self):
        """
        Do aggregation of data to return the resource hosted zone name.

        Returns:
            str: Resource hosted zone name.
        """

        return self.raw["hosted_zone"]["name"]

    @property
    def hosted_zone_id(self):
        """
        Do aggregation of data to return the resource hosted zone id.

        Returns:
            str: Resource hosted zone id.
        """

        return self.raw["hosted_zone"]["id"]

    @property
    def access(self):
        """
        Do aggregation of data to return if the resource is private.

        Returns:
            str: Returns 'public' or 'private'
        """

        if self.raw["hosted_zone"]["private"]:
            return "private"
        else:
            return "public"

    @property
    def monitor(self):
        """
        Do aggregation of data to return if the resource is being monitor.

        Returns:
            str: Resource type.
        """

        try:
            monitor = self._get_field("monitor", "str")
            if monitor not in [True, False]:
                monitor = "unknown"
        except KeyError:
            monitor = "unknown"

        return monitor

    def short_print(self):
        """
        Override parent method to do aggregation of data to print the id of the
        resource.

        Is less verbose than print and describe methods.

        Returns:
            stdout: Prints 'id: name' of the resource.
        """

        print(self.id)

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Value:")
        for value in self.value:
            print("    {}".format(value))
        print("  Type: {}".format(self.type))
        print("  Zone: {}".format(self.hosted_zone_id))
        print("  Access: {}".format(self.access))
        print("  Description: {}".format(self.description))
        print("  Destroy: {}".format(self.to_destroy))

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            Record value
            Record type

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the parent searches
        if super().search(search_string):
            return True

        # Search by value
        for value in self.value:
            if re.match(search_string, value):
                return True

        # Search by type
        if re.match(search_string, self.type, re.IGNORECASE):
            return True

        return False


class S3(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the S3 resources.

    Public properties:
        name: Returns the name of the resource.
        monitor: Returns if the resource is monitor.
        print: Prints information of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("Name", "str")

    @property
    def monitor(self):
        """
        Do aggregation of data to return if the resource is being monitor.

        Returns:
            str: Resource type.
        """

        try:
            monitor = self._get_field("monitor", "str")
            if monitor not in [True, False]:
                monitor = "unknown"
        except KeyError:
            monitor = "unknown"

        return monitor

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Description: {}".format(self.description))
        print("  Permissions: desired/real"),
        print(
            "      READ: {}/{}".format(
                self.raw["desired_permissions"]["read"], self.raw["permissions"]["READ"]
            )
        ),
        print(
            "      WRITE: {}/{}".format(
                self.raw["desired_permissions"]["write"],
                self.raw["permissions"]["WRITE"],
            )
        ),
        print("  Environment: {}".format(self.raw["environment"])),
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy))


class SecurityGroup(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the SecurityGroup resources.

    Public methods:
        print: Prints information of the resource.
        is_related: Return if the security group is related with the contents
            of a regular expression.
        is_synchronized: Check if the real state of the security group
            is the same as the expected.
        search: Extend the parent search method to include security_groups
            specific search.

    Private methods:
        _print_security_rule: print the information of a security rule.
        _is_security_rule_related: Return if the security rule is related with
            the contents of a regular expression.

    Public properties:
        name: Returns the name of the resource.
        vpc: VPC id of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("GroupName")

    def is_synchronized(self):
        """
        Check if the real state of the security group is the same as the
        expected.

        Returns:
            bool: If the state is synchronized.
        """

        if (
            self.raw["ingress"] == self.raw["IpPermissions"]
            and self.raw["egress"] == self.raw["IpPermissionsEgress"]
        ):
            return True
        return False

    def _print_security_group_pairs_information(self, security_group_pair):
        """
        Print the information of the UserIdGroupPairs security rule part.

        Input:
            security_group_pair (dict): Security group pair dictionary,
                for example:

                {
                    'GroupId': 'sg-yyyyyyyy',
                    'UserId': 'zzzzzzzzzzzz',
                    'Description': 'sg description',
                }

        Return:
            stdout: Print the information with a defined format.
        """
        try:
            print(
                "      - {}: {}".format(
                    security_group_pair["GroupId"], security_group_pair["Description"],
                )
            )
        except KeyError:
            print("      - {}".format(security_group_pair["GroupId"]))

    def _print_security_rule(self, security_rule):
        """
        Print the information of a security rule.

        Input:
            security_rule (dict): Security rule dictionary, for example:

                {
                    'FromPort': 0,
                    'IpProtocol': 'tcp',
                    'IpRanges': [],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 65535,
                }

        Return:
            stdout: Print the information with a defined format.
        """
        protocol = security_rule["IpProtocol"].upper()

        if protocol == "ICMP":
            port_string = ""
        elif protocol == "-1":
            protocol = "All Traffic"
            port_string = ""
        else:
            if security_rule["FromPort"] == security_rule["ToPort"]:
                port_string = security_rule["FromPort"]
            else:
                port_string = "{}-{}".format(
                    security_rule["FromPort"], security_rule["ToPort"],
                )

        print("    {}: {}".format(protocol, port_string))

        try:
            if len(security_rule["IpRanges"]) > 0:
                for cidr in security_rule["IpRanges"]:
                    print("      - {}".format(cidr["CidrIp"]))
        except KeyError:
            pass

        try:
            if len(security_rule["UserIdGroupPairs"]) > 0:
                for security_group in security_rule["UserIdGroupPairs"]:
                    self._print_security_group_pairs_information(security_group)

        except KeyError:
            pass

    def _is_security_rule_related(self, regexp, security_rule):
        """
        Return if the security rule is related with the contents of a
        regular expression.

        It checks in the security group rules CIDRs, related security groups
        and ports.

        Input:
            regexp (dict): Regular expression to test.
            security_rule (dict): Security rule dictionary, for example:

                {
                    'FromPort': 0,
                    'IpProtocol': 'tcp',
                    'IpRanges': [],
                    'Ipv6Ranges': [],
                    'PrefixListIds': [],
                    'ToPort': 65535,
                }

        Return:
            bool: If it's related
        """
        # Check regular expression in the associated IPv4s.
        for cidr in security_rule["IpRanges"]:
            if re.match(regexp, cidr["CidrIp"]):
                return True

        # Check regular expression in the associated ports.
        try:
            port_to_test = int(regexp)
            if (
                port_to_test >= security_rule["FromPort"]
                and port_to_test <= security_rule["ToPort"]
            ):
                return True
        except ValueError:
            pass

        # Check regular expression in the associated security groups
        for security_group in security_rule["UserIdGroupPairs"]:
            if re.match(regexp, security_group["GroupId"]):
                return True

    def is_related(self, regexp):
        """
        Return if the security group is related with the contents of a
        regular expression.

        It checks in the security group rules CIDRs, related security groups
        and ports.

        Input:
            regexp (dict): Regular expression to test.

        Return:
            bool: If it's related
        """

        for security_rule in self._get_field("IpPermissions"):
            if self._is_security_rule_related(regexp, security_rule):
                return True

        for security_rule in self._get_field("IpPermissionsEgress"):
            if self._is_security_rule_related(regexp, security_rule):
                return True

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy)),
        print("  Synchronized: {}".format(str(self.is_synchronized())))
        print("  Region: {}".format(self._get_field("region", "str")))
        print("  VPC: {}".format(self.vpc))
        print("  Ingress:")
        for security_rule in self._get_field("IpPermissions"):
            self._print_security_rule(security_rule)
        print("  Egress:")
        for security_rule in self._get_field("IpPermissionsEgress"):
            self._print_security_rule(security_rule)

    def search(self, search_string):
        """
        Extend the parent search method to include security_groups specific
        search.

        Extend to search by:
            CIDR in security group ingress and egress rules.
            Security groups in security group ingress and egress rules.
            Ports in security group ingress and egress rules.
            VPC.

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches.
        if super().search(search_string):
            return True

        # Search by CIDR, port and security groups in the rules.
        if self.is_related(search_string):
            return True

        # Search by VPC.
        if self.vpc is not None and re.match(search_string, self.vpc):
            return True

        return False

    @property
    def vpc(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_optional_field("VpcId")


class VPC(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the VPC resources.

    Public methods:
        print: Prints information of the resource.

    Public properties:
        name: Returns the name of the record.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        try:
            for tag in self.raw["Tags"]:
                if tag["Key"] == "Name":
                    return tag["Value"]
        except KeyError:
            pass
        except TypeError:
            pass
        return "none"

    @property
    def cidr(self):
        """
        Do aggregation of data to return the VPC CIDR.

        Returns:
            str: CIDR.
        """

        return self._get_field("CidrBlock", "str")

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state)),
        print("  Destroy: {}".format(self.to_destroy)),
        print("  Region: {}".format(self._get_field("region", "str")))
        print("  CIDR: {}".format(self.cidr))
