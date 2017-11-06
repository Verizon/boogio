# ----------------------------------------------------------------------------
# Copyright (C) 2017 Verizon.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ----------------------------------------------------------------------------

'''AWSReporter report definitions.'''

# pylint: disable=invalid-name

import boogio.aws_reporter as aws_reporter

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EC2 report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
ec2_report = aws_reporter.ReportDefinition(
    name='EC2Instances',
    entity_type='ec2',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Tags:Name'},
        {'path': 'site-specific.genus'},
        {'path': 'KeyName'},
        {'path': 'LaunchTime'},
        {'path': 'Tags:aws:cloudformation:stack-name'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:AppVersion'},
        {'path': 'Tags:ContactEmail'},
        {'path': 'Tags:Email'},
        {'path': 'Tags:CreatedBy'},
        {'path': 'Tags:Owner'},
        {'path': 'Tags:Environment'},
        {'path': 'Tags:Role'},
        {'path': 'Tags:aws:elasticmapreduce:job-flow-id'},
        {'path': 'Placement:AvailabilityZone'},
        {'path': 'ImageId'},
        {'path': 'InstanceId'},
        {'path': 'InstanceType'},
        {'path': 'State.Name'},
        {'path': 'PublicIpAddress'},
        {'path': 'PrivateIpAddress'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'VpcId.VpcId'},
        {'path': 'VpcId.IsDefault'},
        {'path': 'SubnetId.Tags:Name'},
        {'path': 'SubnetId.CidrBlock'},
        {'path': 'SubnetId.SubnetId'},
        {'path': 'SubnetId.State'},
        {'path': 'SubnetId.AvailableIpAddressCount'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VpcId.Tags:Name', 'Tags:Name', 'site-specific.genus', 'InstanceId',
        'KeyName', 'State.Name',
        'PublicIpAddress', 'PrivateIpAddress', 'Placement:AvailabilityZone',
        'Tags:AppName', 'Tags:AppVersion',
        'Tags:aws:cloudformation:stack-name',
        'ImageId', 'LaunchTime',
        'VpcId.VpcId', 'VpcId.IsDefault',
        'InstanceType', "Tags:aws:elasticmapreduce:job-flow-id",
        'Tags:ContactEmail', 'Tags:Email',
        'SubnetId.CidrBlock', 'SubnetId.Tags:Name',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EC2 existential report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
ec2_existential_report = aws_reporter.ReportDefinition(
    name='EC2Existential',
    entity_type='ec2',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'Tags:Name'},
        {'path': 'KeyName'},
        {'path': 'InstanceId'},
        {'path': 'State.Name'},
        {'path': 'Placement:AvailabilityZone'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:AppVersion'},
        {'path': 'ImageId'},
        {'path': 'LaunchTime'},
        {'path': 'VpcId.VpcId'},
        {'path': 'VpcId.IsDefault'},
        {'path': 'InstanceType'},
        {'path': 'Tags:aws:elasticmapreduce:job-flow-id'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VpcId.Tags:Name', 'Tags:Name', 'InstanceId', 'State.Name',
        'KeyName',
        'Placement:AvailabilityZone',
        'Tags:AppName', 'Tags:AppVersion',
        'Tags:aws:cloudformation:stack-name',
        'ImageId', 'LaunchTime', 'VpcId.VpcId', 'VpcId.IsDefault',
        'InstanceType'
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EC2 security group report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO: Multiple branching cross-flattening is suspicious.
ec2_security_group_report = aws_reporter.ReportDefinition(
    name='EC2-SG',
    entity_type='ec2',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'Tags:Name'},
        {'path': 'InstanceId'},
        {'path': 'State.Name'},
        {'path': 'Placement:AvailabilityZone'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:AppVersion'},
        {'path': 'ImageId'},
        {'path': 'LaunchTime'},
        {'path': 'VpcId.VpcId'},
        {'path': 'VpcId.IsDefault'},
        {'path': 'InstanceType'},

        {'path': 'SecurityGroups.[].GroupId'},
        {'path': 'SecurityGroups.[].GroupName'},
        {'path': 'SecurityGroups.[].Description'},
        {'path': 'NetworkInterfaces.[].NetworkInterfaceId'},
        {'path': 'NetworkInterfaces.[].Description'},
        {'path': 'NetworkInterfaces.[].PrivateIpAddress'},
        {'path': 'NetworkInterfaces.[].Groups.[].GroupId'},
        {'path': 'NetworkInterfaces.[].Groups.[].GroupName'},
        {'path': 'NetworkInterfaces.[].Groups.[].Description'},

        {'path': 'Tags:aws:elasticmapreduce:job-flow-id'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'Tags:Name', 'InstanceId', 'VpcId.Tags:Name',
        'SecurityGroups.GroupId', 'SecurityGroups.GroupName',
        'SecurityGroups.Description',
        'NetworkInterfaces.NetworkInterfaceId',
        'NetworkInterfaces.Description',
        'NetworkInterfaces.PrivateIpAddress',
        'NetworkInterfaces.Groups.GroupId',
        'NetworkInterfaces.Groups.GroupName',
        'NetworkInterfaces.Groups.Description',
        'State.Name',
        'PublicIpAddress', 'PrivateIpAddress', 'Placement:AvailabilityZone',
        'Tags:AppName', 'Tags:AppVersion',
        'Tags:aws:cloudformation:stack-name',
        'ImageId', 'LaunchTime', 'VpcId.VpcId', 'VpcId.IsDefault',
        'InstanceType', "Tags:aws:elasticmapreduce:job-flow-id",
        'Tags:ContactEmail', 'Tags:Email',
        'SubnetId.CidrBlock', 'SubnetId.Tags:Name',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EC2 security group and network interface
# security group detailed reports.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
ec2_security_group_deep_report = ec2_security_group_report.copy()

ec2_security_group_deep_report.name = 'EC2-SG-deep'
# TODO: Multiple branching cross-flattening is suspicious.
ec2_security_group_deep_report.prune_specs.extend([
    {'path': 'SecurityGroups.[].IpPermissions.[].FromPort'},
    {'path': 'SecurityGroups.[].IpPermissions.[].IpProtocol'},
    {'path': 'SecurityGroups.[].IpPermissions.[].IpRanges.[].CidrIp'},
    {'path': 'SecurityGroups.[].IpPermissions.[].PrefixListIds'},
    {'path': 'SecurityGroups.[].IpPermissions.[].ToPort'},
    {
        'path': (
            'SecurityGroups.[].IpPermissions.[].UserIdGroupPairs.[]'
            '.GroupId'
            )},
    {
        'path': (
            'SecurityGroups.[].IpPermissions.[].UserIdGroupPairs.[]'
            '.UserId'
            )},
    ])
ec2_security_group_deep_report.default_column_order.extend(
    [
        'SecurityGroups.IpPermissions.IpRanges.CidrIp',
        'SecurityGroups.IpPermissions.IpProtocol',
        'SecurityGroups.IpPermissions.FromPort',
        'SecurityGroups.IpPermissions.ToPort',
        'SecurityGroups.IpPermissions.UserIdGroupPairs.GroupId',
        'SecurityGroups.IpPermissions.UserIdGroupPairs.UserId',
        'SecurityGroups.IpPermissions.PrefixListIds',
        ]
    )

ec2_network_interface_security_group_deep_report = (
    ec2_security_group_report.copy()
    )

ec2_network_interface_security_group_deep_report.name = 'EC2-NI-SG-deep'
# TODO: Multiple branching cross-flattening is suspicious.
ec2_network_interface_security_group_deep_report.prune_specs.extend(
    [

        # Network interface security groups.
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].FromPort'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].IpProtocol'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].IpRanges.[].CidrIp'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].PrefixListIds'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].ToPort'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].UserIdGroupPairs.[].GroupId'
                )},
        {
            'path': (
                'NetworkInterfaces.[].Groups.[].IpPermissions'
                '.[].UserIdGroupPairs.[].UserId'
                )},
        ]
    )
ec2_network_interface_security_group_deep_report.default_column_order.extend(
    [

        'NetworkInterfaces.Groups.IpPermissions.IpRanges.CidrIp',
        'NetworkInterfaces.Groups.IpPermissions.IpProtocol',
        'NetworkInterfaces.Groups.IpPermissions.FromPort',
        'NetworkInterfaces.Groups.IpPermissions.ToPort',
        'NetworkInterfaces.Groups.IpPermissions.UserIdGroupPairs.GroupId',
        'NetworkInterfaces.Groups.IpPermissions.UserIdGroupPairs.UserId',
        'NetworkInterfaces.Groups.IpPermissions.PrefixListIds',
        ]
    )


ec2_tags_report = aws_reporter.ReportDefinition(
    name='EC2InstanceTags',
    entity_type='ec2',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Tags:Name'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:AppVersion'},
        {'path': 'Tags:ContactEmail'},
        {'path': 'Tags:CreatedBy'},
        {'path': 'Tags:Email'},
        {'path': 'Tags:Environment'},
        {'path': 'Tags:Owner'},
        {'path': 'Tags:Role'},
        {'path': 'Tags:aws:autoscaling:groupName'},
        {'path': 'Tags:aws:cloudformation:logical-id'},
        {'path': 'Tags:aws:cloudformation:stack-id'},
        {'path': 'Tags:aws:cloudformation:stack-name'},
        {'path': 'Tags:aws:elasticmapreduce:instance-group-role'},
        {'path': 'Tags:aws:elasticmapreduce:job-flow-id'},
        {'path': 'Tags:funnel:mirror:uri-template'},
        {'path': 'Tags:funnel:target:name'},
        {'path': 'Tags:funnel:target:qualifier'},
        {'path': 'Tags:funnel:target:version'},
        {'path': 'Tags:funnel:telemetry:uri-template'},
        {'path': 'Tags:jenkins_slave_type'},
        {'path': 'Tags:revision'},
        {'path': 'Tags:servicename'},
        {'path': 'Tags:servicetypes'},
        {'path': 'Tags:type'},
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ELB reports.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
elb_report = aws_reporter.ReportDefinition(
    name='LoadBalancers',
    entity_type='elb',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'LoadBalancerName'},
        {'path': 'site-specific.genus'},
        {'path': 'VPCId.Tags:Name'},
        {'path': 'Scheme'},
        {'path': 'CreatedTime'},
        {
            'path': 'AvailabilityZones',
            'value_refiner': lambda x: ' '.join([str(y) for y in x])
            },
        {'path': 'DNSName'},
        {
            'path': 'DNSIpAddress.INET.[]',
            'flatten_leaves': True,  # TODO: Does this still do anything?
            },
        {
            'path': 'Instances',
            'value_refiner': len
            },
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VPCId.Tags:Name', 'LoadBalancerName', 'site-specific.genus',
        'DNSIpAddress.INET', 'Scheme', 'CreatedTime',
        'DNSName', 'AvailabilityZones', 'Instances',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
elb_instances_report = aws_reporter.ReportDefinition(
    name='LoadBalancerInstances',
    entity_type='elb',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'LoadBalancerName'},
        {'path': 'site-specific.genus'},
        {'path': 'VPCId.Tags:Name'},
        {'path': 'Scheme'},
        {'path': 'CreatedTime'},
        {
            'path': 'AvailabilityZones',
            'value_refiner': lambda x: ' '.join([str(y) for y in x])
            },
        {'path': 'DNSName'},
        {'path': 'Instances.[].InstanceId'},
        {'path': 'Instances.[].KeyName'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VPCId.Tags:Name', 'LoadBalancerName', 'site-specific.genus',
        'Scheme', 'CreatedTime',
        'DNSName', 'AvailabilityZones',
        'Instances.InstanceId', 'Instances.KeyName'
        ]
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
elb_listener_report = elb_report.copy()
elb_listener_report.name = 'LoadBalancerListeners'
# TODO: Multiple branching cross-flattening is suspicious.
elb_listener_report.prune_specs.extend([
    {'path': 'ListenerDescriptions.[].Listener.InstancePort'},
    {'path': 'ListenerDescriptions.[].Listener.InstanceProtocol'},
    {'path': 'ListenerDescriptions.[].Listener.LoadBalancerPort'},
    {'path': 'ListenerDescriptions.[].Listener.Protocol'},
    {'path': 'ListenerDescriptions.[].Listener.SSLCertificateId'},
    {'path': 'ListenerDescriptions.[].PolicyNames'},
    ])
elb_listener_report.default_column_order.extend([
    'ListenerDescriptions.Listener.InstancePort',
    'ListenerDescriptions.Listener.InstanceProtocol',
    'ListenerDescriptions.Listener.LoadBalancerPort',
    'ListenerDescriptions.Listener.Protocol',
    'ListenerDescriptions.Listener.SSLCertificateId',
    'ListenerDescriptions.PolicyNames',
    ])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ELB SecurityGroups report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
elb_security_group_deep_report = elb_listener_report.copy()
elb_security_group_deep_report.name = "ELB-SG-deep"
# TODO: Multiple branching cross-flattening is suspicious.
elb_security_group_deep_report.prune_specs.extend([
    {'path': 'SecurityGroups.[].GroupId'},
    {'path': 'SecurityGroups.[].GroupName'},
    {'path': 'SecurityGroups.[].Description'},
    {'path': 'SecurityGroups.[].IpPermissions.[].FromPort'},
    {'path': 'SecurityGroups.[].IpPermissions.[].IpProtocol'},
    {'path': 'SecurityGroups.[].IpPermissions.[].IpRanges.[].CidrIp'},
    {'path': 'SecurityGroups.[].IpPermissions.[].PrefixListIds'},
    {'path': 'SecurityGroups.[].IpPermissions.[].ToPort'},
    {
        'path': (
            'SecurityGroups.[].IpPermissions.[].UserIdGroupPairs.[]'
            '.GroupId'
            )},
    {
        'path': (
            'SecurityGroups.[].IpPermissions.[].UserIdGroupPairs.[]'
            '.UserId'
            )},
    ])
elb_security_group_deep_report.default_column_order.extend([
    'SecurityGroups.GroupId',
    'SecurityGroups.GroupName',
    'SecurityGroups.Description',
    'SecurityGroups.IpPermissions.IpProtocol',
    'SecurityGroups.IpPermissions.IpRanges.CidrIp',
    'SecurityGroups.IpPermissions.FromPort',
    'SecurityGroups.IpPermissions.ToPort',
    'SecurityGroups.IpPermissions.PrefixListIds',
    'SecurityGroups.IpPermissions.UserIdGroupPairs.GroupId',
    'SecurityGroups.IpPermissions.UserIdGroupPairs.UserId',
    ])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ELB Certificate Report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
elb_cert_report = aws_reporter.ReportDefinition(
    name='LoadBalancerCerts',
    entity_type='elb',
    prune_specs=[
        # pylint: disable=line-too-long
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'LoadBalancerName'},
        {'path': 'site-specific.genus'},
        {'path': 'DNSName'},
        {'path': 'ListenerDescriptions.[].Listener.InstancePort'},
        {'path': 'ListenerDescriptions.[].Listener.SSLCertificateId'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VPCId.Tags:Name', 'LoadBalancerName', 'site-specific.genus',
        'DNSIpAddress.INET', 'Scheme', 'DNSName',
        'AvailabilityZones', 'Instances',
        ]
    )
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
asg_report = aws_reporter.ReportDefinition(
    name='AutoScaling',
    entity_type='autoscaling',
    prune_specs=[
        # pylint: disable=line-too-long
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'AutoScalingGroupName'},
        {'path': 'CreatedTime'},
        {'path': 'DefaultCooldown'},
        {'path': 'DesiredCapacity'},
        {'path': 'HealthCheckGracePeriod'},
        {'path': 'HealthCheckType'},
        {'path': 'Instances.[].InstanceId'},
        {'path': 'LoadBalancerNames.[]'},
        {'path': 'MaxSize'},
        {'path': 'MinSize'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:AppVersion'},
        {'path': 'Tags:ApplicationTags'},
        {'path': 'Tags:Environment'},
        {'path': 'Tags:Monitoring'},
        # {'path': 'Tags:NAME'},
        {'path': 'Tags:Name'},
        {'path': 'Tags:servicename'},
        {'path': 'Tags:servicetypes'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'AutoScalingGroupName', 'CreatedTime',
        'MinSize', 'DesiredCapacity', 'MaxSize',
        'DefaultCooldown', 'HealthCheckGracePeriod', 'HealthCheckType',
        'LoadBalancerNames', 'Instances.InstanceId',
        'Tags:AppName', 'Tags:AppVersion', 'Tags:ApplicationTags',
        'Tags:Environment', 'Tags:Monitoring',
        # 'Tags:NAME',
        'Tags:Name',
        'Tags:servicename', 'Tags:servicetypes',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EIP report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
eip_report = aws_reporter.ReportDefinition(
    name='ElasticIPs',
    entity_type='eip',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'PublicIp'},
        {'path': 'PrivateIpAddress'},
        {'path': 'InstanceId'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'InstanceId', 'PublicIp', 'PrivateIpAddress',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# VPC report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
vpc_report = aws_reporter.ReportDefinition(
    name='VPCs',
    entity_type='vpc',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'VpcId'},
        {'path': 'Tags:Name'},
        {'path': 'CidrBlock'},
        {'path': 'IsDefault'},
        {'path': 'State'},
        {'path': 'DhcpOptionsId'},
        {'path': 'InstanceTenancy'},
        {'path': 'Tags:aws:cloudformation:logical-id'},
        {'path': 'Tags:aws:cloudformation:stack-id'},
        {'path': 'Tags:aws:cloudformation:stack-name'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'VpcId', 'Tags:Name', 'CidrBlock',
        'IsDefault', 'State', 'DhcpOptionsId', 'InstanceTenancy',
        'Tags:aws:cloudformation:logical-id',
        'Tags:aws:cloudformation:stack-id',
        'Tags:aws:cloudformation:stack-name',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Subnet report.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
subnet_report = aws_reporter.ReportDefinition(
    name='Subnets',
    entity_type='subnet',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Tags:Name'},
        {'path': 'SubnetId'},
        {'path': 'CidrBlock'},
        {'path': 'AvailabilityZone'},
        {'path': 'AvailableIpAddressCount'},
        {'path': 'VpcId.VpcId'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'VpcId.CidrBlock'},
        {'path': 'DefaultForAz'},
        {'path': 'MapPublicIpOnLaunch'},
        {'path': 'State'},
        {'path': 'Tags:aws:cloudformation:logical-id'},
        {'path': 'Tags:aws:cloudformation:stack-id'},
        {'path': 'Tags:aws:cloudformation:stack-name'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'Tags:Name', 'SubnetId', 'CidrBlock', 'AvailabilityZone',
        'AvailableIpAddressCount',
        'VpcId.VpcId', 'VpcId.Tags:Name', 'VpcId.CidrBlock',
        'DefaultForAz', 'MapPublicIpOnLaunch', 'State',
        'Tags:aws:cloudformation:logical-id',
        'Tags:aws:cloudformation:stack-id',
        'Tags:aws:cloudformation:stack-name',
        ]
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SG reports.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO: Multiple branching cross-flattening is suspicious.
security_group_report = aws_reporter.ReportDefinition(
    name='SecurityGroups',
    entity_type='security_group',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'GroupId'},
        {'path': 'GroupName'},
        {'path': 'Tags:Name'},
        {'path': 'Description'},
        {'path': 'VpcId.VpcId'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'VpcId.CidrBlock'},
        {'path': 'Tags:AppName'},
        {'path': 'IpPermissions.[].IpRanges.[].CidrIp'},
        {'path': 'IpPermissions.[].IpProtocol'},
        {'path': 'IpPermissions.[].FromPort'},
        {'path': 'IpPermissions.[].ToPort'},
        {'path': 'IpPermissions.[].UserIdGroupPairs.[].UserId'},
        {'path': 'IpPermissions.[].UserIdGroupPairs.[].GroupId'},
        {'path': 'IpPermissions.[].PrefixListIds'},
        {'path': 'IpPermissionsEgress.[].IpRanges.[].CidrIp'},
        {'path': 'IpPermissionsEgress.[].IpProtocol'},
        {'path': 'IpPermissionsEgress.[].FromPort'},
        {'path': 'IpPermissionsEgress.[].ToPort'},
        {'path': 'IpPermissionsEgress.[].UserIdGroupPairs.[].UserId'},
        {'path': 'IpPermissionsEgress.[].UserIdGroupPairs.[].GroupId'},
        {'path': 'IpPermissionsEgress.[].PrefixListIds'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'GroupId', 'GroupName', 'Tags:Name', 'Description',
        'VpcId.VpcId', 'VpcId.Tags:Name', 'VpcId.CidrBlock',
        'Tags:AppName',
        'IpPermissions.IpRanges.CidrIp', 'IpPermissions.IpProtocol',
        'IpPermissions.FromPort', 'IpPermissions.ToPort',
        'IpPermissions.UserIdGroupPairs.GroupId',
        'IpPermissions.UserIdGroupPairs.UserId',
        'IpPermissions.PrefixListIds',
        'IpPermissionsEgress.IpRanges.CidrIp',
        'IpPermissionsEgress.IpProtocol',
        'IpPermissionsEgress.FromPort', 'IpPermissionsEgress.ToPort',
        'IpPermissionsEgress.UserIdGroupPairs.GroupId',
        'IpPermissionsEgress.UserIdGroupPairs.UserId',
        'IpPermissionsEgress.PrefixListIds',
        ]
    )

security_group_admin_report = aws_reporter.ReportDefinition(
    name='SecurityGroupAdmin',
    entity_type='security_group',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'GroupId'},
        {'path': 'GroupName'},
        {'path': 'Tags:Name'},
        {'path': 'Description'},
        {'path': 'OwnerId'},
        {'path': 'VpcId'},
        {'path': 'VpcId.Tags:Name'},
        {'path': 'Tags:AppName'},
        {'path': 'Tags:CreatedBy'},
        {'path': 'Tags:Environment'},
        {'path': 'Tags:Name'},
        {'path': 'Tags:aws:cloudformation:stack-name'},
        {'path': 'Tags:funnel:target:name'},
        {'path': 'Tags:funnel:target:qualifier'},
        {'path': 'Tags:servicename'},
        {'path': 'Tags:servicetypes'},
        {'path': 'Tags:type'},
        ],
    default_column_order=[
        'meta.profile_name', 'meta.region_name',
        'GroupId', 'GroupName', 'Tags:Name', 'Description', 'OwnerId',
        'VpcId', 'VpcId.Tags:Name',
        'Tags:Environment',
        'Tags:Name',
        'Tags:type',
        'Tags:AppName', 'Tags:CreatedBy',
        'Tags:servicename',
        'Tags:servicetypes',
        'Tags:aws:cloudformation:stack-name',
        'Tags:funnel:target:name',
        'Tags:funnel:target:qualifier',
        ]
    )


nacl_report = aws_reporter.ReportDefinition(
    name='NetworkACL',
    entity_type='network_acl',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'NetworkAclId'},
        {'path': 'Tags:Name'},
        {'path': 'IsDefault'},
        {'path': 'VpcId'},
        {'path': 'Entries.[].CidrBlock'},
        {'path': 'Entries.[].Egress'},
        {'path': 'Entries.[].PortRange.From'},
        {'path': 'Entries.[].PortRange.To'},
        {'path': 'Entries.[].PortRangeDesc'},
        {'path': 'Entries.[].Protocol'},
        {'path': 'Entries.[].RuleAction'},
        {'path': 'Entries.[].RuleNumber'},
        {'path': 'Associations.[].NetworkAclAssociationId'},
        {'path': 'Associations.[].SubnetId'},
        ],
    default_column_order=[
        '',
        ]
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IAM Reports.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
iam_group_report = aws_reporter.ReportDefinition(
    name='IAMGroups',
    entity_type='iam',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Groups.[].Arn'},
        {'path': 'Groups.[].CreateDate'},
        {'path': 'Groups.[].GroupId'},
        {'path': 'Groups.[].GroupName'},
        {'path': 'Groups.[].Path'},
        ]
    )

# TODO: Multiple branching cross-flattening is suspicious.
iam_instance_profiles_report = aws_reporter.ReportDefinition(
    name='IAMInstanceProfiles',
    entity_type='iam',
    prune_specs=[
        # pylint: disable=line-too-long
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'InstanceProfiles.[].Arn'},
        {'path': 'InstanceProfiles.[].CreateDate'},
        {'path': 'InstanceProfiles.[].InstanceProfileId'},
        {'path': 'InstanceProfiles.[].InstanceProfileName'},
        {'path': 'InstanceProfiles.[].Path'},
        {'path': 'InstanceProfiles.[].Roles.[].Arn'},
        {
            'path': (
                'InstanceProfiles.[].Roles.[].AssumeRolePolicyDocument'
                '.Statement.[].Action'
                )},
        {
            'path': (
                'InstanceProfiles.[].Roles.[].AssumeRolePolicyDocument'
                '.Statement.[].Effect'
                )},
        {
            'path': (
                'InstanceProfiles.[].Roles.[].AssumeRolePolicyDocument'
                '.Statement.[].Principal.Service'
                )},
        {
            'path': (
                'InstanceProfiles.[].Roles.[].AssumeRolePolicyDocument'
                '.Statement.[].Sid'
                )},
        {
            'path': (
                'InstanceProfiles.[].Roles.[].AssumeRolePolicyDocument'
                '.Version'
                )},
        {'path': 'InstanceProfiles.[].Roles.[].CreateDate'},
        {'path': 'InstanceProfiles.[].Roles.[].Path'},
        {'path': 'InstanceProfiles.[].Roles.[].RoleId'},
        {'path': 'InstanceProfiles.[].Roles.[].RoleName'},
        ]
    )

# TODO: Multiple branching cross-flattening is suspicious.
iam_policies_report = aws_reporter.ReportDefinition(
    name='IAMPolicies',
    entity_type='iam',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Policies.[].Arn'},
        {'path': 'Policies.[].AttachmentCount'},
        {'path': 'Policies.[].CreateDate'},
        {'path': 'Policies.[].DefaultVersionId'},
        {'path': 'Policies.[].IsAttachable'},
        {'path': 'Policies.[].Path'},
        {'path': 'Policies.[].PolicyGroups'},
        {'path': 'Policies.[].PolicyId'},
        {'path': 'Policies.[].PolicyName'},
        {'path': 'Policies.[].PolicyRoles'},
        {'path': 'Policies.[].PolicyUsers'},
        {'path': 'Policies.[].PolicyUsers.[].UserName'},
        {'path': 'Policies.[].UpdateDate'},
        {'path': 'Policies.[].Versions.[].CreateDate'},
        {'path': 'Policies.[].Versions.[].IsDefaultVersion'},
        {'path': 'Policies.[].Versions.[].VersionId'},

        ]
    )

# TODO: Multiple branching cross-flattening is suspicious.
iam_roles_report = aws_reporter.ReportDefinition(
    name='IAMRoles',
    entity_type='iam',
    prune_specs=[
        # pylint: disable=line-too-long
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Roles.[].Arn'},
        {'path': 'Roles.[].AssumeRolePolicyDocument.Statement.[].Action'},
        {'path': 'Roles.[].AssumeRolePolicyDocument.Statement.[].Effect'},
        {
            'path': (
                'Roles.[].AssumeRolePolicyDocument.Statement'
                '.[].Principal.Service'
                )},
        {
            'path': (
                'Roles.[].AssumeRolePolicyDocument.Statement'
                '.[].Principal.Service.[]'
                )},
        {'path': 'Roles.[].AssumeRolePolicyDocument.Statement.[].Sid'},
        {'path': 'Roles.[].AssumeRolePolicyDocument.Version'},

        {'path': 'Roles.[].AttachedPolicies'},
        {'path': 'Roles.[].CreateDate'},
        {'path': 'Roles.[].InstanceProfiles'},
        {'path': 'Roles.[].InstanceProfiles.[].Arn'},
        {'path': 'Roles.[].InstanceProfiles.[].CreateDate'},
        {'path': 'Roles.[].InstanceProfiles.[].InstanceProfileId'},
        {'path': 'Roles.[].InstanceProfiles.[].InstanceProfileName'},
        {'path': 'Roles.[].InstanceProfiles.[].Path'},
        {'path': 'Roles.[].InstanceProfiles.[].Roles.[].Arn'},
        {
            'path': (
                'Roles.[].InstanceProfiles.[].Roles.[]'
                '.AssumeRolePolicyDocument.Statement.[].Action'
                )},
        {
            'path': (
                'Roles.[].InstanceProfiles.[].Roles.[]'
                '.AssumeRolePolicyDocument.Statement.[].Effect'
                )},
        {
            'path': (
                'Roles.[].InstanceProfiles.[].Roles.[]'
                '.AssumeRolePolicyDocument.Statement.[].Principal.Service'
                )},
        {
            'path': (
                'Roles.[].InstanceProfiles.[].Roles.[]'
                '.AssumeRolePolicyDocument.Statement.[].Sid'
                )},
        {
            'path': (
                'Roles.[].InstanceProfiles.[].Roles.[]'
                '.AssumeRolePolicyDocument.Version'
                )},
        {'path': 'Roles.[].InstanceProfiles.[].Roles.[].CreateDate'},
        {'path': 'Roles.[].InstanceProfiles.[].Roles.[].Path'},
        {'path': 'Roles.[].InstanceProfiles.[].Roles.[].RoleId'},
        {'path': 'Roles.[].InstanceProfiles.[].Roles.[].RoleName'},
        {'path': 'Roles.[].Path'},
        {'path': 'Roles.[].PolicyNames.[]'},
        {'path': 'Roles.[].RoleId'},
        {'path': 'Roles.[].RoleName'},
        ]
    )

iam_server_certs_report = aws_reporter.ReportDefinition(
    name='IAMServerCerts',
    entity_type='iam',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'ServerCertificateMetadataList.[].Arn'},
        {'path': 'ServerCertificateMetadataList.[].Expiration'},
        {'path': 'ServerCertificateMetadataList.[].Path'},
        {'path': 'ServerCertificateMetadataList.[].ServerCertificateId'},
        {'path': 'ServerCertificateMetadataList.[].ServerCertificateName'},
        {'path': 'ServerCertificateMetadataList.[].UploadDate'},
        ]
    )

# TODO: Multiple branching cross-flattening is suspicious.
iam_users_report = aws_reporter.ReportDefinition(
    name='IAMUsers',
    entity_type='iam',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Users.[].Arn'},
        {'path': 'Users.[].CreateDate'},
        {'path': 'Users.[].PasswordLastUsed'},
        {'path': 'Users.[].Path'},
        {'path': 'Users.[].UserId'},
        {'path': 'Users.[].UserName'},
        {'path': 'Users.[].AccessKeys.[].CreateDate'},
        {'path': 'Users.[].AccessKeys.[].Status'},
        {'path': 'Users.[].AccessKeys.[].UserName'},
        {'path': 'Users.[].AttachedPolicies.[].PolicyArn'},
        {'path': 'Users.[].AttachedPolicies.[].PolicyName'},
        {'path': 'Users.[].Groups.[].Arn'},
        {'path': 'Users.[].Groups.[].CreateDate'},
        {'path': 'Users.[].Groups.[].GroupId'},
        {'path': 'Users.[].Groups.[].GroupName'},
        {'path': 'Users.[].Groups.[].Path'},
        {'path': 'Users.[].PolicyNames.[]'},

        ]
    )

iam_keys_report = aws_reporter.ReportDefinition(
    name='IAMAccessKeys',
    entity_type='iam',
    prune_specs=[
        {'path': 'meta.profile_name'},
        {'path': 'meta.region_name'},
        {'path': 'Users.[].AccessKeys.[].AccessKeyId'},
        {'path': 'Users.[].AccessKeys.[].CreateDate'},
        {'path': 'Users.[].AccessKeys.[].Status'},
        {'path': 'Users.[].AccessKeys.[].UserName'},
        ]
    )


# # This should be a list of all the predefined specs listed in this file.
# canned_specs = [
#     ec2_report,
#     ec2_existential_report,
#     ec2_tags_report,
#     elb_report,
#     elb_cert_report,
#     eip_report,
#     security_group_report,
#     security_group_admin_report,
#     vpc_report,
#     subnet_report,
#     iam_users_report,
#     iam_server_certs_report,
#     iam_policies_report,
#     iam_roles_report,
#     iam_group_report,
#     iam_instance_profiles_report,
#     iam_keys_report,
#     ]
