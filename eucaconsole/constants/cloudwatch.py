# -*- coding: utf-8 -*-
"""
Common constants for CloudWatch

"""

METRIC_TYPES = [
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupDesiredCapacity', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupInServiceInstances', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupMaxSize', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupMinSize', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupPendingInstances', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupTerminatingInstances', 'unit': ''},
    {'namespace': 'AWS/AutoScaling', 'name': 'GroupTotalInstances', 'unit': ''},
    {'namespace': 'AWS/EBS', 'name': 'VolumeIdleTime', 'unit': 'Seconds'},
    {'namespace': 'AWS/EBS', 'name': 'VolumeQueueLength', 'unit': ''},
    {'namespace': 'AWS/EBS', 'name': 'VolumeReadBytes', 'unit': 'Bytes'},
    {'namespace': 'AWS/EBS', 'name': 'VolumeReadOps', 'unit': ''},
    {'namespace': 'AWS/EBS', 'name': 'VolumeTotalReadTime', 'unit': 'Seconds'},
    {'namespace': 'AWS/EBS', 'name': 'VolumeWriteOps', 'unit': ''},
    {'namespace': 'AWS/EBS', 'name': 'VolumeTotalWriteTime', 'unit': 'Seconds'},
    {'namespace': 'AWS/EC2', 'name': 'CPUUtilization', 'unit': 'Percent'},
    {'namespace': 'AWS/EC2', 'name': 'DiskReadBytes', 'unit': 'Bytes'},
    {'namespace': 'AWS/EC2', 'name': 'DiskReadOps', 'unit': ''},
    {'namespace': 'AWS/EC2', 'name': 'DiskWriteBytes', 'unit': 'Bytes'},
    {'namespace': 'AWS/EC2', 'name': 'DiskWriteOps', 'unit': ''},
    {'namespace': 'AWS/EC2', 'name': 'NetworkIn', 'unit': 'Bytes'},
    {'namespace': 'AWS/EC2', 'name': 'NetworkOut', 'unit': 'Bytes'},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_Backend_2XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_Backend_3XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_Backend_4XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_Backend_5XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_ELB_4XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HTTPCode_ELB_5XX', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'Latency', 'unit': 'Seconds'},
    {'namespace': 'AWS/ELB', 'name': 'RequestCount', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'HealthyHostCount', 'unit': ''},
    {'namespace': 'AWS/ELB', 'name': 'UnHealthyHostCount', 'unit': ''},
]


# Maps simplified dimension keys to dimension names (for dict key in MetricAlarm().dimensions attr)
METRIC_DIMENSION_NAMES = {
    'availability_zone': 'AvailabilityZone',
    'image': 'ImageId',
    'instance': 'InstanceId',
    'instance_type': 'InstanceType',
    'load_balancer': 'LoadBalancerName',
    'scaling_group': 'AutoScalingGroupName',
    'volume': 'VolumeId',
}

# Maps simplified dimension keys to dimension input fields (in forms.alarms.CloudWatchAlarmCreateForm)
METRIC_DIMENSION_INPUTS = {
    'availability_zone': 'availability_zone',
    'image': 'image_id',
    'instance': 'instance_id',
    'instance_type': 'instance_type',
    'load_balancer': 'load_balancer_name',
    'scaling_group': 'scaling_group_name',
    'volume': 'volume_id',
}

