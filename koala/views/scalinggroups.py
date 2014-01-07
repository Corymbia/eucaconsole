# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS scaling groups

"""
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.scalinggroups import ScalingGroupDeleteForm
from ..models import Notification
from ..models import LandingPageFilter
from ..views import LandingPageView, BaseView 


class ScalingGroupsView(LandingPageView):
    def __init__(self, request):
        super(ScalingGroupsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/scalinggroups'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default

    @view_config(route_name='scalinggroups', renderer='../templates/scalinggroups/scalinggroups.pt')
    def scalinggroups_landing(self):
        json_items_endpoint = self.request.route_url('scalinggroups_json')
        self.filter_keys = ['availability_zones', 'launch_config', 'name', 'placement_group']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
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
        for group in self.get_items():
            scalinggroups.append(dict(
                availability_zones=', '.join(group.availability_zones),
                desired_capacity=group.desired_capacity,
                launch_config=group.launch_config_name,
                max_size=group.max_size,
                min_size=group.min_size,
                name=group.name,
                placement_group=group.placement_group,
                termination_policies=', '.join(group.termination_policies),
            ))
        return dict(results=scalinggroups)

    def get_items(self):
        conn = self.get_connection(conn_type='autoscale')
        return conn.get_all_groups() if conn else []


class ScalingGroupView(BaseView):
    """Views for single ScalingGroup"""
    TEMPLATE = '../templates/scalinggroups/scalinggroup_view.pt'

    def __init__(self, request):
        super(ScalingGroupView, self).__init__(request)
        self.conn = self.get_connection(conn_type='autoscale')
        self.scalinggroup = self.get_scalinggroup()
        self.delete_form = ScalingGroupDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            scalinggroup=self.scalinggroup,
            delete_form=self.delete_form,
        )

    def get_scalinggroup(self):
        scalinggroup_param = self.request.matchdict.get('id')
        scalinggroups_param = [scalinggroup_param]
        scalinggroups = self.conn.get_all_groups(names=scalinggroups_param)
        scalinggroups = scalinggroups[0] if scalinggroups else None
        return scalinggroups 

    @view_config(route_name='scalinggroup_view', renderer=TEMPLATE)
    def scalinggroup_view(self):
        self.scalinggroup.availability_zones_str = ', '.join(self.scalinggroup.availability_zones)
        self.scalinggroup.termination_policies_str = ', '.join(self.scalinggroup.termination_policies)
        return self.render_dict

    @view_config(route_name='scalinggroup_delete', request_method='POST', renderer=TEMPLATE)
    def scalinggroup_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            try:
                self.conn.delete_auto_scaling_group(name, force_delete=True)
                prefix = _(u'Successfully deleted scalinggroup')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            location = self.request.route_url('scalinggroups')
            return HTTPFound(location=location)

        return self.render_dict

