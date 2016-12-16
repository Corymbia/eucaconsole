# -*- coding: utf-8 -*-
# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Forms for VPC resources

"""
from wtforms import SelectField, StringField, validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager, TextEscapedField
from ..views import TaggedItemView


INTERNET_GATEWAY_HELP_TEXT = _(
    'An internet gateway allows communication between instances in your VPC and the Internet.'
    'An internet gateway must be attached to a VPC if you wish to create one or more public subnets in the VPC.'
)

CIDR_BLOCK_REGEX = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' \
                    '([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'


class VPCsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""

    def __init__(self, request, ec2_conn=None, cloud_type='euca', **kwargs):
        super(VPCsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.cloud_type = cloud_type
        self.ec2_choices_manager = ChoicesManager(conn=ec2_conn)
        self.facets = [
            {'name': 'state', 'label': _('State'), 'options': self.get_state_choices()},
            {'name': 'availability_zone', 'label': _('Availability zone'),
                'options': self.get_availability_zone_choices()},
        ]

    @staticmethod
    def get_state_choices():
        return [
            {'key': 'available', 'label': _(u'Available')},
            {'key': 'pending', 'label': _(u'Pending')},
        ]

    def get_availability_zone_choices(self):
        return self.get_options_from_choices(self.ec2_choices_manager.availability_zones(self.region, add_blank=False))


class VPCForm(BaseSecureForm):
    """VPC form (to update an existing VPC)"""
    name_error_msg = _('Not a valid name')
    name = TextEscapedField(label=_('Name'))
    internet_gateway = SelectField(label=_('Internet gateway'))

    def __init__(self, request, vpc_conn=None, vpc=None, vpc_internet_gateway=None, **kwargs):
        super(VPCForm, self).__init__(request, **kwargs)
        self.vpc_conn = vpc_conn
        self.vpc = vpc
        self.vpc_internet_gateway = vpc_internet_gateway
        self.name.error_msg = self.name_error_msg
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.internet_gateway.choices = self.get_internet_gateway_choices()

        if vpc is not None:
            self.name.data = vpc.tags.get('Name', '')
            if self.vpc_internet_gateway is None:
                self.internet_gateway.data = 'None'
            else:
                self.internet_gateway.data = self.vpc_internet_gateway.id

    def get_internet_gateway_choices(self):
        choices_list = []
        if self.vpc and self.vpc_internet_gateway:
            # Add the existing IGW if necessary, as we're going to filter out attached internet gateways later
            choices_list.append(
                (TaggedItemView.get_display_name(self.vpc_internet_gateway), self.vpc_internet_gateway.id)
            )
        igw_choices = self.vpc_choices_manager.internet_gateways()
        for choice in igw_choices:
            choices_list.append(choice)
        return sorted(set(choices_list))


class VPCDeleteForm(BaseSecureForm):
    pass


class VPCMainRouteTableForm(BaseSecureForm):
    """VPC form to set main route table"""
    route_table = SelectField(label=_('Route table'))

    def __init__(self, request, vpc_conn=None, vpc=None, vpc_main_route_table=None, **kwargs):
        super(VPCMainRouteTableForm, self).__init__(request, **kwargs)
        vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.route_table.choices = vpc_choices_manager.vpc_route_tables(vpc=vpc, add_blank=False)

        if vpc_main_route_table is not None:
            self.route_table.data = vpc_main_route_table.id


class CreateInternetGatewayForm(BaseSecureForm):
    new_igw_name = StringField(label=_('Name'))


class CreateVPCForm(BaseSecureForm):
    name_error_msg = _('Not a valid name')
    name = StringField(label=_('Name'))
    cidr_block_error_msg = _('A valid CIDR block is required')
    cidr_block = StringField(
        label=_('CIDR block'),
        validators=[
            validators.InputRequired(message=cidr_block_error_msg),
            validators.Regexp(CIDR_BLOCK_REGEX),
        ]
    )
    internet_gateway = SelectField(label=_('Internet gateway'))

    def __init__(self, request, vpc_conn=None, **kwargs):
        super(CreateVPCForm, self).__init__(request, **kwargs)
        self.vpc_conn = vpc_conn
        self.vpc_choices_manager = ChoicesManager(conn=vpc_conn)
        self.internet_gateway.choices = self.vpc_choices_manager.internet_gateways(hide_attached=True)
        self.name.error_msg = self.name_error_msg
        self.cidr_block.error_msg = self.cidr_block_error_msg
        self.name.help_text = _(
            'Creates a tag with key = Name and value set to the specified string.'
        )
        self.cidr_block.help_text = _(
            'The range of IPs to be used for your VPC, in CIDR format (e.g. 10.0.0.0/24).<br /><br />'
            'WARNING: Creating a VPC with a CIDR block that conflicts with the pubic IPs of the cloud'
            'may lead to unpredictable behavior.'
        )
        self.internet_gateway.help_text = INTERNET_GATEWAY_HELP_TEXT
