"""Test the AWS adapter particular cases."""

from clinv.adapters.aws import build_security_group_rule_data


def test_build_sg_rules_extracts_description_from_ip_range() -> None:
    """
    Given: A security group with a description in the IpRange
    When: build_security_group_rule_data is called
    Then: The description is extracted
    """
    input_ = {
        "IpProtocol": "tcp",
        "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Rule description"}],
        "Ipv6Ranges": [],
        "PrefixListIds": [],
        "FromPort": 443,
        "ToPort": 443,
    }

    result = build_security_group_rule_data(input_)

    assert result["description"] == "Rule description"


def test_build_sg_rules_extracts_description_from_ipv6_range() -> None:
    """
    Given: A security group with a description in the Ipv6Range
    When: build_security_group_rule_data is called
    Then: The description is extracted
    """
    input_ = {
        "IpProtocol": "tcp",
        "Ipv6Ranges": [{"CidrIp": "0.0.0.0/0", "Description": "Rule description"}],
        "IpRanges": [],
        "PrefixListIds": [],
        "FromPort": 443,
        "ToPort": 443,
    }

    result = build_security_group_rule_data(input_)

    assert result["description"] == "Rule description"


def test_build_sg_rules_extracts_description_from_sg_range() -> None:
    """
    Given: A security group with a description in the UserIdGroupPairs
    When: build_security_group_rule_data is called
    Then: The description is extracted
    """
    input_ = {
        "IpProtocol": "tcp",
        "Ipv6Ranges": [],
        "IpRanges": [],
        "PrefixListIds": [],
        "UserIdGroupPairs": [{"GroupId": "sg-xxxx", "Description": "Rule description"}],
        "FromPort": 443,
        "ToPort": 443,
    }

    result = build_security_group_rule_data(input_)

    assert result["description"] == "Rule description"
    assert result["sg_range"] == ["sg-xxxx"]


def test_build_sg_rules_extracts_icmp_ports() -> None:
    """
    Given: A security group with a protocol of ICMP
    When: build_security_group_rule_data is called
    Then: The ports of the security group rule are -2
    """
    input_ = {
        "IpProtocol": "icmp",
        "Ipv6Ranges": [],
        "IpRanges": [],
        "PrefixListIds": [],
        "UserIdGroupPairs": [],
    }

    result = build_security_group_rule_data(input_)

    assert result["protocol"] == "ICMP"
    assert result["ports"] == [-2]
