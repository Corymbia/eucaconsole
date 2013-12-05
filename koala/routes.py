# -*- coding: utf-8 -*-
"""
URL dispatch routes

The route names and patterns are listed here.
The routes are wired up to view callables via the view_config decorator, which attaches a view to the route_name.

For example, the 'instances' route name is connected to the Instances landing page as follows...

    @view_config(route_name='instances', renderer='../templates/instances/instances.pt')
    def instances_landing(self):
        pass

"""
from collections import namedtuple


# Simple container to hold a route name and pattern
Route = namedtuple('Route', ['name', 'pattern'])

urls = [
    # Dashboard
    Route(name='dashboard', pattern='/'),
    Route(name='dashboard_json', pattern='/dashboard/json'),
    # Login/logout
    Route(name='login', pattern='/login'),
    Route(name='logout', pattern='/logout'),
    # Common
    Route(name='region_select', pattern='/region/select'),
    # Images
    Route(name='images', pattern='/images'),
    Route(name='images_json', pattern='/images/json'),
    # Instances
    Route(name='instances', pattern='/instances'),
    Route(name='instances_json', pattern='/instances/json'),
    Route(name='instance_launch', pattern='/instances/launch'),
    Route(name='instance_view', pattern='/instances/{id}'),
    Route(name='instance_update', pattern='/instances/{id}/update'),
    Route(name='instance_reboot', pattern='/instances/{id}/reboot'),
    Route(name='instance_start', pattern='/instances/{id}/start'),
    Route(name='instance_stop', pattern='/instances/{id}/stop'),
    Route(name='instance_terminate', pattern='/instances/{id}/terminate'),
    Route(name='instance_state_json', pattern='/instances/{id}/state/json'),
    Route(name='instance_volumes', pattern='/instances/{id}/volumes'),
    Route(name='instance_volumes_json', pattern='/instances/{id}/volumes/json'),
    Route(name='instance_volume_attach', pattern='/instances/{id}/volume/attach'),
    Route(name='instance_volume_detach', pattern='/instances/{id}/volume/{volume_id}/detach'),
    # Scaling Groups
    Route(name='scalinggroups', pattern='/scalinggroups'),
    Route(name='scalinggroups_json', pattern='/scalinggroups/json'),
    # Launch Configurations
    Route(name='launchconfigs', pattern='/launchconfigs'),
    Route(name='launchconfigs_json', pattern='/launchconfigs/json'),
    # Volumes
    Route(name='volumes', pattern='/volumes'),
    Route(name='volumes_json', pattern='/volumes/json'),
    # Snapshots
    Route(name='snapshots', pattern='/snapshots'),
    Route(name='snapshots_json', pattern='/snapshots/json'),
    # Security Groups
    Route(name='securitygroups', pattern='/securitygroups'),
    Route(name='securitygroups_json', pattern='/securitygroups/json'),
    Route(name='securitygroup_create', pattern='/securitygroups/create'),
    Route(name='securitygroup_view', pattern='/securitygroups/{id}'),
    Route(name='securitygroup_update', pattern='/securitygroups/{id}/update'),
    Route(name='securitygroup_delete', pattern='/securitygroups/{id}/delete'),
    # Key pairs
    Route(name='keypairs', pattern='/keypairs'),
    Route(name='keypairs_json', pattern='/keypairs/json'),
    Route(name='keypair_view', pattern='/keypairs/{id}'),
    # IP Addresses
    Route(name='ipaddresses', pattern='/ipaddresses'),
    Route(name='ipaddresses_json', pattern='/ipaddresses/json'),
    Route(name='ipaddress_view', pattern='/ipaddresses/{public_ip}'),
    Route(name='ipaddress_associate', pattern='/ipaddresses/{public_ip}/associate'),
    Route(name='ipaddress_disassociate', pattern='/ipaddresses/{public_ip}/disassociate'),
    Route(name='ipaddress_release', pattern='/ipaddresses/{public_ip}/release'),
]
