# -*- coding: utf-8 -*-
"""
Forms for Scaling Group 

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager


class ScalingGroupEditForm(BaseSecureForm):
    """Edit Scaling Group form"""
    launch_config_error_msg = _(u'Launch configuration is required')
    launch_config = wtforms.SelectField(
        label=_(u'Launch configuration'),
        validators=[
            validators.InputRequired(message=launch_config_error_msg),
        ],
    )
    availability_zones_error_msg = _(u'At least one availability zone is required')
    availability_zones = wtforms.SelectMultipleField(
        label=_(u'Availability zones'),
        validators=[
            validators.InputRequired(message=availability_zones_error_msg),
        ],
    )
    desired_capacity_error_msg = _(u'Field is required')
    desired_capacity = wtforms.IntegerField(
        label=_(u'Desired'),
        validators=[
            validators.InputRequired(message=desired_capacity_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    max_size_error_msg = _(u'Max is required')
    max_size = wtforms.IntegerField(
        label=_(u'Max'),
        validators=[
            validators.InputRequired(message=max_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    min_size_error_msg = _(u'Min is required')
    min_size = wtforms.IntegerField(
        label=_(u'Min'),
        validators=[
            validators.InputRequired(message=min_size_error_msg),
            validators.NumberRange(min=0, max=99),
        ],
    )
    health_check_type_error_msg = _(u'Health check type is required')
    health_check_type = wtforms.SelectField(
        label=_(u'Type'),
        validators=[
            validators.InputRequired(message=health_check_type_error_msg),
        ],
    )
    health_check_period_error_msg = _(u'Health check grace period is required')
    health_check_period = wtforms.IntegerField(
        label=_(u'Grace period (seconds)'),
        validators=[
            validators.InputRequired(message=health_check_period_error_msg),
        ],
    )
    default_cooldown_error_msg = _(u'Default cooldown period is required')
    default_cooldown = wtforms.IntegerField(
        label=_(u'Default cooldown period (seconds)'),
        validators=[
            validators.InputRequired(message=default_cooldown_error_msg),
        ],
    )
    termination_policies_error_msg = _(u'At least one termination policy is required')
    termination_policies = wtforms.SelectMultipleField(
        label=_(u'Termination policies'),
        validators=[
            validators.InputRequired(message=termination_policies_error_msg),
        ],
    )

    def __init__(self, request, scaling_group=None, autoscale_conn=None, ec2_conn=None, launch_configs=None, **kwargs):
        super(ScalingGroupEditForm, self).__init__(request, **kwargs)
        self.scaling_group = scaling_group
        self.autoscale_conn = autoscale_conn
        self.ec2_conn = ec2_conn
        self.launch_configs = launch_configs
        self.choices_manager = ChoicesManager(conn=ec2_conn)
        self.set_error_messages()
        self.set_choices()

        if scaling_group is not None:
            self.launch_config.data = scaling_group.launch_config_name
            self.availability_zones.data = scaling_group.availability_zones
            self.desired_capacity.data = int(scaling_group.desired_capacity) if scaling_group.desired_capacity else 1
            self.max_size.data = int(scaling_group.max_size) if scaling_group.max_size else 1
            self.min_size.data = int(scaling_group.min_size) if scaling_group.min_size else 0
            self.health_check_type.data = scaling_group.health_check_type
            self.health_check_period.data = scaling_group.health_check_period
            self.default_cooldown.data = scaling_group.default_cooldown
            self.termination_policies.data = scaling_group.termination_policies

    def set_choices(self):
        self.launch_config.choices = self.get_launch_config_choices()
        self.health_check_type.choices = self.get_healthcheck_type_choices()
        self.availability_zones.choices = self.get_availability_zone_choices()
        self.termination_policies.choices = self.get_termination_policy_choices()

    def set_error_messages(self):
        self.launch_config.error_msg = self.launch_config_error_msg
        self.availability_zones.error_msg = self.availability_zones_error_msg
        self.desired_capacity.error_msg = self.desired_capacity_error_msg
        self.max_size.error_msg = self.max_size_error_msg
        self.min_size.error_msg = self.min_size_error_msg
        self.health_check_type.error_msg = self.health_check_type_error_msg
        self.health_check_period.error_msg = self.health_check_period_error_msg
        self.default_cooldown.error_msg = self.default_cooldown_error_msg
        self.termination_policies.error_msg = self.termination_policies_error_msg

    def get_launch_config_choices(self):
        choices = []
        launch_configs = self.launch_configs
        if launch_configs is None:
            launch_configs = self.autoscale_conn.get_all_launch_configurations()
        for launch_config in launch_configs:
            choices.append((launch_config.name, launch_config.name))
        if self.scaling_group:
            launch_config_name = self.scaling_group.launch_config_name
            choices.append((launch_config_name, launch_config_name))
        return sorted(set(choices))

    def get_availability_zone_choices(self):
        return self.choices_manager.availability_zones()

    @staticmethod
    def get_healthcheck_type_choices():
        return [(u'EC2', u'EC2'), (u'ELB', _(u'Load Balancer'))]

    @staticmethod
    def get_termination_policy_choices():
        return (
            (u'Default', _(u'Default')),
            (u'OldestInstance', _(u'Oldest instance')),
            (u'NewestInstance', _(u'Newest instance')),
            (u'OldestLaunchConfiguration', _(u'Oldest launch configuration')),
            (u'ClosestToNextInstanceHour', _(u'Closest to next instance hour')),
        )


class ScalingGroupDeleteForm(BaseSecureForm):
    """ScalingGroup deletion form.
       Only need to initialize as a secure form to generate CSRF token
    """
    pass


