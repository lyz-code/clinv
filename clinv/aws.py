
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
        try:
            return self.instance['InstanceId']
        except KeyError:
            pass

    @property
    def type(self):
        try:
            return self.instance['InstanceType']
        except KeyError:
            pass

    def print(self):
        print('- Name: {}'.format(self.name))
        print('  ID: {}'.format(self.id))
        print('  State: {}'.format(self.state))
        print('  Type: {}'.format(self.type))
        print('  SecurityGroups: {}'.format(self.security_groups))
        print('  PrivateIP: {}'.format(self.private_ips))
        print('  PublicIP: {}'.format(self.public_ips))
