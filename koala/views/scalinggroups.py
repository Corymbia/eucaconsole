# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
from operator import attrgetter
import simplejson as json
import time

from boto.ec2.autoscale import AutoScalingGroup, ScalingPolicy
from boto.ec2.autoscale.tag import Tag
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.response import Response
from pyramid.view import view_config

from ..forms.alarms import CloudWatchAlarmCreateForm
from ..forms.scalinggroups import ScalingGroupDeleteForm, ScalingGroupEditForm, ScalingGroupCreateForm
from ..forms.scalinggroups import ScalingGroupPolicyCreateForm, ScalingGroupPolicyDeleteForm
from ..models import Notification
from ..views import LandingPageView, BaseView


class ScalingGroupsView(LandingPageView):
    TEMPLATE = '../templates/scalinggroups/scalinggroups.pt'

    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='scalinggroups', renderer=TEMPLATE, request_method='GET')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_url('scalinggroups_json')
        self.filter_keys = ['availability_zones', 'launch_config', 'name', 'placement_group']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
            dict(key='-status', name=_(u'Health status')),
            dict(key='-current_instances_count', name=_(u'Current instances')),
            dict(key='launch_config', name=_(u'Launch configuration')),
            dict(key='availability_zones', name=_(u'Availability zones')),
        ]
        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )


class ScalingGroupsJsonView(BaseView):
    @view_config(route_name='scalinggroups_json', renderer='json', request_method='GET')
    def scalinggroups_json(self):
        scalinggroups = []
        try:
            items = self.get_items()
        except BotoServerError as err:
            return Response(status=err.status, body=err.message)
        for group in items:
            group_instances = group.instances or []
            all_healthy = all(instance.health_status == 'Healthy' for instance in group_instances)
            scalinggroups.append(dict(
                availability_zones=', '.join(sorted(group.availability_zones)),
                load_balancers=', '.join(sorted(group.load_balancers)),
                desired_capacity=group.desired_capacity,
                launch_config=group.launch_config_name,
                max_size=group.max_size,
                min_size=group.min_size,
                name=group.name,
                placement_group=group.placement_group,
                termination_policies=', '.join(group.termination_policies),
                current_instances_count=len(group_instances),
                status='Healthy' if all_healthy else 'Unhealthy',
            ))
        return dict(results=scalinggroups)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups() if conn else []


class BaseScalingGroupView(BaseView):
    def __init__(self, request):
        super(BaseScalingGroupView, self).__init__(request)
        self.autoscale_conn = self.get_connection(conn_type='autoscale')
        self.cloudwatch_conn = self.get_connection(conn_type='cloudwatch')
        self.elb_conn = self.get_connection(conn_type='elb')
        self.ec2_conn = self.get_connection()

    def get_scaling_group(self):
        scalinggroup_param = self.request.matchdict.get('id')  # id = scaling_group.name
        scalinggroups_param = [scalinggroup_param]
        scaling_groups = self.autoscale_conn.get_all_groups(names=scalinggroups_param)
        return scaling_groups[0] if scaling_groups else None

    def get_alarms(self):
        if self.cloudwatch_conn:
            return self.cloudwatch_conn.describe_alarms()
        return []

    def parse_tags_param(self, scaling_group_name=None):
        tags_json = self.request.params.get('tags')
        tags_list = json.loads(tags_json) if tags_json else []
        tags = []
        for tag in tags_list:
            tags.append(Tag(
                resource_id=scaling_group_name,
                key=tag.get('name'),
                value=tag.get('value'),
                propagate_at_launch=tag.get('propagate_at_launch', False),
            ))
        return tags


class ScalingGroupView(BaseScalingGroupView):
    """Views for Scaling Group detail page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_view.pt'

    def __init__(self, request):
        super(ScalingGroupView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.edit_form = ScalingGroupEditForm(
            self.request, scaling_group=self.scaling_group, autoscale_conn=self.autoscale_conn, ec2_conn=self.ec2_conn,
            elb_conn=self.elb_conn, formdata=self.request.params or None)
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            edit_form=self.edit_form,
            delete_form=self.delete_form,
            avail_zone_placeholder_text=_(u'Select one or more availability zones...'),
            termination_policies_placeholder_text=_(u'Select one or more termination policies...')
        )

    @view_config(route_name='scalinggroup_view', renderer=TEMPLATE)
    def scalinggroup_view(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_update', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_update(self):
        if self.edit_form.validate():
            location = self.request.route_url('scalinggroup_view', id=self.scaling_group.name)
            try:
                self.update_tags()
                self.update_properties()
                prefix = _(u'Successfully updated scaling group')
                msg = '{0} {1}'.format(prefix, self.scaling_group.name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='scalinggroup_delete', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_delete(self):
        if self.delete_form.validate():
            location = self.request.route_url('scalinggroups')
            name = self.request.params.get('name')
            try:
                # Need to shut down instances prior to scaling group deletion
                self.scaling_group.shutdown_instances()
                time.sleep(3)
                self.autoscale_conn.delete_auto_scaling_group(name)
                time.sleep(1)
                prefix = _(u'Successfully deleted scaling group')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def update_tags(self):
        updated_tags_list = self.parse_tags_param(scaling_group_name=self.scaling_group.name)
        # Delete existing tags first
        if self.scaling_group.tags:
            self.autoscale_conn.delete_tags(self.scaling_group.tags)
        self.autoscale_conn.create_or_update_tags(updated_tags_list)

    def update_properties(self):
        self.scaling_group.desired_capacity = self.request.params.get('desired_capacity', 1)
        self.scaling_group.launch_config_name = self.request.params.get('launch_config')
        self.scaling_group.availability_zones = self.request.params.getall('availability_zones')  # getall = multiselect
        self.scaling_group.termination_policies = self.request.params.getall('termination_policies')
        self.scaling_group.max_size = self.request.params.get('max_size', 1)
        self.scaling_group.min_size = self.request.params.get('min_size', 0)
        self.scaling_group.health_check_type = self.request.params.get('health_check_type')
        self.scaling_group.health_check_period = self.request.params.get('health_check_period', 120)
        self.scaling_group.default_cooldown = self.request.params.get('default_cooldown', 120)
        self.scaling_group.update()


class ScalingGroupInstancesView(BaseScalingGroupView):
    """View for Scaling Group Manage Instances page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_instances.pt'

    def __init__(self, request):
        super(ScalingGroupInstancesView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.instances = self.get_instances()
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            instances=self.instances,
        )

    @view_config(route_name='scalinggroup_instances', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_instances(self):
        return self.render_dict

    def get_instances(self):
        if self.scaling_group.instances is None:
            return []
        return sorted(self.scaling_group.instances, key=attrgetter('instance_id'))


class ScalingGroupPoliciesView(BaseScalingGroupView):
    """View for Scaling Group Policies page"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_policies.pt'

    def __init__(self, request):
        super(ScalingGroupPoliciesView, self).__init__(request)
        self.scaling_group = self.get_scaling_group()
        self.policies = self.get_policies()
        self.alarms = self.get_alarms()
        self.metrics = self.cloudwatch_conn.list_metrics()
        self.create_form = ScalingGroupPolicyCreateForm(
            self.request, scaling_group=self.scaling_group, alarms=self.alarms, formdata=self.request.params or None)
        self.delete_form = ScalingGroupPolicyDeleteForm(self.request, formdata=self.request.params or None)
        self.alarm_form = CloudWatchAlarmCreateForm(
            self.request, metrics=self.metrics, formdata=self.request.params or None)
        self.render_dict = dict(
            scaling_group=self.scaling_group,
            create_form=self.create_form,
            delete_form=self.delete_form,
            alarm_form=self.alarm_form,
            policies=self.policies,
            scale_down_text=_(u'Scale down by'),
            scale_up_text=_(u'Scale up by'),
        )

    @view_config(route_name='scalinggroup_policies', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_policies(self):
        return self.render_dict

    @view_config(route_name='scalinggroup_policy_create', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_policy_create(self):
        location = self.request.route_url('scalinggroup_policies', id=self.scaling_group.name)
        if self.create_form.validate():
            adjustment_amount = self.request.params.get('adjustment_amount')
            adjustment_direction = self.request.params.get('adjustment_direction', 'up')
            scaling_adjustment = adjustment_amount
            if adjustment_direction == 'down':
                scaling_adjustment = -adjustment_direction
            scaling_policy = ScalingPolicy(
                name=self.request.params.get('name'),
                as_name=self.scaling_group.name,
                adjustment_type=self.request.params.get('adjustment_type'),
                scaling_adjustment=scaling_adjustment,
                cooldown=self.request.params.get('cooldown'),
            )
            try:
                # Create scaling policy
                self.autoscale_conn.create_scaling_policy(scaling_policy)
                created_scaling_policy = self.autoscale_conn.get_all_policies(
                    as_group=self.scaling_group.name, policy_names=[scaling_policy.name])[0]
                # Attach policy to alarm
                alarm_name = self.request.params.get('alarm')
                alarm = self.cloudwatch_conn.describe_alarms(alarm_names=[alarm_name])[0]
                # FIXME: Properly attach a policy to an alarm
                # TODO: Detect if an alarm has 5 scaling policies attached to it and abort accordingly
                if created_scaling_policy.policy_arn not in alarm.alarm_actions:
                    alarm.add_alarm_action(created_scaling_policy.policy_arn)
                alarm.update()
                prefix = _(u'Successfully created scaling group policy')
                msg = '{0} {1}'.format(prefix, scaling_policy.name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='scalinggroup_policy_delete', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_policy_delete(self):
        if self.delete_form.validate():
            location = self.request.route_url('scalinggroup_policies', id=self.scaling_group.name)
            policy_name = self.request.params.get('name')
            try:
                self.autoscale_conn.delete_policy(policy_name, autoscale_group=self.scaling_group.name)
                prefix = _(u'Successfully deleted scaling group policy')
                msg = '{0} {1}'.format(prefix, policy_name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_policies(self):
        policies = self.autoscale_conn.get_all_policies(as_group=self.scaling_group.name)
        return sorted(policies)


class ScalingGroupWizardView(BaseScalingGroupView):
    """View for Create Scaling Group wizard"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_wizard.pt'

    def __init__(self, request):
        super(ScalingGroupWizardView, self).__init__(request)
        self.request = request
        self.create_form = ScalingGroupCreateForm(
            self.request, autoscale_conn=self.autoscale_conn, ec2_conn=self.ec2_conn,
            elb_conn=self.elb_conn, formdata=self.request.params or None)
        self.render_dict = dict(
            create_form=self.create_form,
            avail_zones_placeholder_text=_(u'Select availability zones...')
        )

    @view_config(route_name='scalinggroup_new', renderer=TEMPLATE, request_method='GET')
    def scalinggroup_new(self):
        """Displays the Launch Instance wizard"""
        return self.render_dict

    @view_config(route_name='scalinggroup_create', renderer=TEMPLATE, request_method='POST')
    def scalinggroup_create(self):
        """Handles the POST from the Create Scaling Group wizard"""
        if self.create_form.validate():
            try:
                scaling_group_name = self.request.params.get('name')
                scaling_group = AutoScalingGroup(
                    name=scaling_group_name,
                    launch_config=self.request.params.get('launch_config'),
                    availability_zones=self.request.params.getall('availability_zones'),
                    load_balancers=self.request.params.getall('load_balancers'),
                    # default_cooldown=None,  # TODO: Implement
                    health_check_type=self.request.params.get('health_check_type'),
                    health_check_period=self.request.params.get('health_check_period'),
                    desired_capacity=self.request.params.get('desired_capacity'),
                    min_size=self.request.params.get('min_size'),
                    max_size=self.request.params.get('max_size'),
                    tags=self.parse_tags_param(scaling_group_name=scaling_group_name),
                    # termination_policies=self.request.params.get('policies'),  # TODO: Implement
                )
                self.autoscale_conn.create_auto_scaling_group(scaling_group)
                msg = _(u'Successfully created scaling group')
                msg += ' {0}'.format(scaling_group.name)
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                location = self.request.route_url('scalinggroup_view', id=scaling_group.name)
                return HTTPFound(location=location)
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
                self.request.session.flash(msg, queue=queue)
                location = self.request.route_url('scalinggroups')
                return HTTPFound(location=location)
        return self.render_dict
