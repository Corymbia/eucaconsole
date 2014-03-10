# -*- coding: utf-8 -*-
"""
Base Forms

IMPORTANT: All forms needing CSRF protection should inherit from BaseSecureForm

"""
from pyramid.i18n import TranslationString as _
from wtforms.ext.csrf import SecureForm
import boto
from boto.exception import BotoServerError

from ..vmtypes import VmType
from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES

BLANK_CHOICE = ('', _(u'select...'))


class BaseSecureForm(SecureForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseSecureForm, self).__init__(**kwargs)

    def generate_csrf_token(self, csrf_context):
        return self.request.session.get_csrf_token()

    def get_errors_list(self):
        """Convenience method to get all form validation errors as a list of message strings"""
        error_messages = []
        for field, errors in self.errors.items():
            msg = '{0}: {1}'.format(field, ', '.join(errors))
            error_messages.append(msg)
        return error_messages


class GenerateFileForm(BaseSecureForm):
    pass


class ChoicesManager(object):
    """Container for form choices reused across the app"""

    def __init__(self, conn=None):
        """"Note: conn param could be a connection object of any type, based on the choices required"""
        self.conn = conn

    #### EC2 connection type choices
    ##

    def availability_zones(self, zones=None, add_blank=True):
        """Returns a list of availability zone choices. Will fetch zones if not passed"""
        choices = []
        zones = zones or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if not zones and self.conn is not None:
            zones = self.conn.get_all_zones()
        for zone in zones:
            choices.append((zone.name, zone.name))
        return sorted(choices)

    def instances(self, instances=None, state=None):
        from ..views import TaggedItemView
        choices = [('', _(u'Select instance...'))]
        instances = instances or []
        if not instances and self.conn is not None:
            instances = self.conn.get_only_instances()
            if self.conn:
                for instance in instances:
                    value = instance.id
                    label = TaggedItemView.get_display_name(instance)
                    if state is None or instance.state == state:
                        choices.append((value, label))
        return choices

    def instance_types(self, cloud_type='euca', add_blank=True, add_description=True):
        """Get instance type (e.g. m1.small) choices
            cloud_type is either 'euca' or 'aws'
        """
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if cloud_type == 'euca':
            if self.conn is not None:
                types = self.conn.get_list('DescribeInstanceTypes', {}, [('item', VmType)], verb='POST')
                for vmtype in types:
                    vmtype_str = '{0}: {1} CPUs, {2} memory (MB), {3} disk (GB,root device)'.format(
                        vmtype.name, vmtype.cores, vmtype.memory, vmtype.disk)
                    vmtype_tuple = vmtype.name, vmtype_str if add_description else vmtype.name
                    choices.append(vmtype_tuple)
            else:
                choices.append(BLANK_CHOICE)
        elif cloud_type == 'aws':
            choices.extend(AWS_INSTANCE_TYPE_CHOICES)
        return choices

    def security_groups(self, securitygroups=None, add_blank=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        security_groups = securitygroups or []
        if not security_groups and self.conn is not None:
            security_groups = self.conn.get_all_security_groups()
        for sgroup in security_groups:
            choices.append((sgroup.name, sgroup.name))
        if not security_groups:
            choices.append(('default', 'default'))
        return sorted(set(choices))

    def keypairs(self, keypairs=None, add_blank=True, no_keypair_option=False):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if no_keypair_option:
            choices.append(('', _(u'No Keypair')))
        keypairs = keypairs or []
        if not keypairs and self.conn is not None:
            keypairs = self.conn.get_all_key_pairs()
        for keypair in keypairs:
            choices.append((keypair.name, keypair.name))
        return sorted(set(choices))

    def elastic_ips(self, instance=None, ipaddresses=None, add_blank=True):
        choices = []  # ('', _(u'None assigned'))]
        ipaddresses = ipaddresses or []
        if not ipaddresses and self.conn is not None:
            ipaddresses = self.conn.get_all_addresses()
        if instance and instance.state == 'running':
            choices.append(('', _(u'Unassign Address')))
        for eip in ipaddresses:
            if eip.instance_id is None:
                choices.append((eip.public_ip, eip.public_ip))
        if instance and instance.ip_address:
            choices.append((instance.ip_address, instance.ip_address))
        if instance and instance.ip_address is None and instance.state == 'stopped':
            choices.append(('none', _(u'no address in stopped state')))
        return sorted(set(choices))

    def kernels(self, kernel_images=None, image=None):
        """Get kernel id choices"""
        choices = [('', _(u'Use default from image'))]
        kernel_images = kernel_images or []
        if not kernel_images and self.conn is not None:
            kernel_images = self.conn.get_all_kernels()  # TODO: cache me
        for kernel_image in kernel_images:
            if kernel_image.id:
                choices.append((kernel_image.id, kernel_image.id))
        if image:
            choices.append((image.kernel_id, image.kernel_id))
        return sorted(set(choices))

    def ramdisks(self, ramdisk_images=None, image=None):
        """Get ramdisk id choices"""
        choices = [('', _(u'Use default from image'))]
        ramdisk_images = ramdisk_images or []
        if not ramdisk_images and self.conn is not None:
            ramdisk_images = self.conn.get_all_ramdisks()  # TODO: cache me
        for ramdisk_image in ramdisk_images:
            if ramdisk_image.id:
                choices.append((ramdisk_image.id, ramdisk_image.id))
        if image and image.ramdisk_id is not None:
            choices.append((image.ramdisk_id, image.ramdisk_id))
        return sorted(set(choices))

    #### AutoScale connection type choices
    ##

    def scaling_groups(self, scaling_groups=None, add_blank=True):
        """Returns a list of scaling group choices"""
        choices = []
        scaling_groups = scaling_groups or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        # Note: self.conn is an ELBConnection
        if not scaling_groups and self.conn is not None:
            scaling_groups = self.conn.get_all_groups()
        for scaling_group in scaling_groups:
            choices.append((scaling_group.name, scaling_group.name))
        return sorted(choices)

    #### ELB connection type choices
    ##

    def load_balancers(self, load_balancers=None, add_blank=True):
        """Returns a list of load balancer choices.  Will fetch load balancers if not passed"""
        choices = []
        try:
            load_balancers = load_balancers or []
            if add_blank:
                choices.append(BLANK_CHOICE)
            # Note: self.conn is an ELBConnection
            if not load_balancers and self.conn is not None:
                load_balancers = self.get_all_load_balancers()
            for load_balancer in load_balancers:
                choices.append((load_balancer.name, load_balancer.name))
        except BotoServerError as ex:
            if ex.reason == "Service Unavailable":
                logging.info("ELB service not available, disabling polling")
            else:
                raise ex
            
        return sorted(choices)

    ### Special version of this to handle case where back end doesn't have ELB configured
    ##

    def get_all_load_balancers(self, load_balancer_names=None):
        params = {}
        if load_balancer_names:
            self.build_list_params(params, load_balancer_names,
                                   'LoadBalancerNames.member.%d')
        http_request = self.conn.build_base_http_request('GET', '/', None,
                                                         params, {}, '',
                                                         self.conn.server_name())
        http_request.params['Action'] = 'DescribeLoadBalancers'
        http_request.params['Version'] = self.conn.APIVersion
        response = self.conn._mexe(http_request, override_num_retries=2)
        body = response.read()
        boto.log.debug(body)
        if not body:
            boto.log.error('Null body %s' % body)
            raise self.conn.ResponseError(response.status, response.reason, body)
        elif response.status == 200:
            obj = boto.resultset.ResultSet([('member', boto.ec2.elb.loadbalancer.LoadBalancer)])
            h = boto.handler.XmlHandler(obj, self.conn)
            import xml.sax;
            xml.sax.parseString(body, h)
            return obj
        else:
            boto.log.error('%s %s' % (response.status, response.reason))
            boto.log.error('%s' % body)
            raise self.conn.ResponseError(response.status, response.reason, body)
        
