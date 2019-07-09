import re


class ClinvGenericResource():
    def __init__(self, raw_data):
        'raw_data: Clinv stripped dictionary containing resource information'

        self.id = [id for id in raw_data.keys()][0]
        self.raw = raw_data[self.id]

    def _get_field(self, key):
        try:
            if self.raw[key] is None:
                raise ValueError(
                    "{} {} key is set to None, ".format(self.id, key) +
                    "please assign it a defined value",
                )
            return self.raw[key]
        except KeyError:
            raise KeyError(
                "{} doesn't have the {} key defined".format(self.id, key)
            )

    def _get_optional_field(self, key):
        try:
            return self.raw[key]
        except KeyError:
            return None

    @property
    def description(self):
        return self._get_field('description')

    @property
    def name(self):
        return self._get_field('name')

    def search(self, search_string):
        # Search by id
        if re.match(search_string, self.id):
            return True

        # Search by name
        if self.name is not None and \
                re.match(search_string, self.name, re.IGNORECASE):
            return True

        # Search by description
        if re.match(search_string, self.description, re.IGNORECASE):
            return True

        return False


class ClinvActiveResource(ClinvGenericResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    def print(self):
        print('{}: {}'.format(self.id, self.name))

    @property
    def state(self):
        return self._get_field('state')

    @property
    def responsible(self):
        return self._get_field('responsible')


class Project(ClinvActiveResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    @property
    def aliases(self):
        return self._get_optional_field('aliases')

    @property
    def services(self):
        return self._get_field('services')

    @property
    def informations(self):
        return self._get_field('informations')

    def search(self, search_string):

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by aliases
        if self.aliases is not None and search_string in self.aliases:
            return True


class Information(ClinvActiveResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)


class Service(ClinvActiveResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)


class ClinvAWSResource(ClinvGenericResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    @property
    def region(self):
        return self._get_field('region')

    def search(self, search_string):
        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by security groups
        if search_string in self.security_groups:
            return True

        # Search by region
        if re.match(search_string, self.region):
            return True

        # Search by type
        if re.match(search_string, self.type):
            return True

        return False


class EC2(ClinvAWSResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    @property
    def name(self):
        try:
            for tag in self.raw['Tags']:
                if tag['Key'] == 'Name':
                    return tag['Value']
        except KeyError:
            pass
        except TypeError:
            pass
        return 'none'

    @property
    def security_groups(self):
        try:
            return [security_group['GroupId']
                    for security_group in self.raw['SecurityGroups']
                    ]
        except KeyError:
            pass

    @property
    def private_ips(self):
        private_ips = []
        try:
            for interface in self.raw['NetworkInterfaces']:
                for address in interface['PrivateIpAddresses']:
                    private_ips.append(address['PrivateIpAddress'])
        except KeyError:
            pass
        return private_ips

    @property
    def public_ips(self):
        public_ips = []
        try:
            for interface in self.raw['NetworkInterfaces']:
                for association in interface['PrivateIpAddresses']:
                    public_ips.append(association['Association']['PublicIp'])
        except KeyError:
            pass
        return public_ips

    @property
    def state(self):
        try:
            return self.raw['State']['Name']
        except KeyError:
            pass

    @property
    def type(self):
        return self._get_field('InstanceType')

    @property
    def state_transition(self):
        return self._get_field('StateTransitionReason')

    def print(self):
        print('- Name: {}'.format(self.name))
        print('  ID: {}'.format(self.id))
        print('  State: {}'.format(self.state))
        if self.state != 'running':
            print('  State Reason: {}'.format(self.state_transition))
        print('  Type: {}'.format(self.type))
        print('  SecurityGroups: {}'.format(self.security_groups))
        print('  PrivateIP: {}'.format(self.private_ips))
        print('  PublicIP: {}'.format(self.public_ips))

    def search(self, search_string):
        # Perform the ClinvAWSResource searches
        if super().search(search_string):
            return True

        # Search by public IP
        if search_string in self.public_ips:
            return True

        # Search by private IP
        if search_string in self.private_ips:
            return True

        # Search by security groups
        if search_string in self.security_groups:
            return True

        # Search by region
        if re.match(search_string, self.region):
            return True

        return False


class RDS(ClinvAWSResource):
    def __init__(self, raw_data):
        super().__init__(raw_data)

    @property
    def name(self):
        return self._get_field('DBInstanceIdentifier')

    @property
    def state(self):
        return self._get_field('DBInstanceStatus')

    @property
    def security_groups(self):
        return self._get_field('DBSecurityGroups')

    @property
    def type(self):
        return self._get_field('DBInstanceClass')
