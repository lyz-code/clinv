import re


class EC2Instance():
    def __init__(self, instance):
        self.instance = instance

    @property
    def name(self):
        try:
            for tag in self.instance['Tags']:
                if tag['Key'] == 'Name':
                    return tag['Value']
        except KeyError:
            pass
        except TypeError:
            pass

    @property
    def security_groups(self):
        try:
            return [security_group['GroupId']
                    for security_group in self.instance['SecurityGroups']
                    ]
        except KeyError:
            pass

    @property
    def private_ips(self):
        private_ips = []
        try:
            for interface in self.instance['NetworkInterfaces']:
                for address in interface['PrivateIpAddresses']:
                    private_ips.append(address['PrivateIpAddress'])
        except KeyError:
            pass
        return private_ips

    @property
    def public_ips(self):
        public_ips = []
        try:
            for interface in self.instance['NetworkInterfaces']:
                for association in interface['PrivateIpAddresses']:
                    public_ips.append(association['Association']['PublicIp'])
        except KeyError:
            pass
        return public_ips

    @property
    def state(self):
        try:
            return self.instance['State']['Name']
        except KeyError:
            pass

    @property
    def id(self):
        return self._get_field('InstanceId')

    @property
    def type(self):
        return self._get_field('InstanceType')

    @property
    def state_transition(self):
        return self._get_field('StateTransitionReason')

    @property
    def description(self):
        return self._get_field('description')

    def _get_field(self, key):
        try:
            return self.instance[key]
        except KeyError:
            pass

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

        # Search by public IP
        if search_string in self.public_ips:
            return True

        # Search by private IP
        if search_string in self.private_ips:
            return True

        # Search by security groups
        if search_string in self.security_groups:
            return True

        return False
