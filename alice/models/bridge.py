from neutronclient.v2_0     import client as nclient
from novaclient             import client as vclient
from keystoneauth1          import loading
from keystoneauth1.identity import v3
from keystoneauth1          import session
from keystoneclient.v3      import client
from os import environ as env

import alice.config as var
import sys
import os


class OpenstackBridge:

    network = var.network
    subnet  = var.subnet

    def __init__(self):
        pass

    # keystone_auth: Connects to keystone database and
    # returns an authenticated client object.
    def keystone_auth(self):
        try:
            auth = v3.Password(auth_url=env['OS_AUTH_URL'],
                               username=env['OS_USERNAME'],
                               password=env['OS_PASSWORD'],
                               user_domain_name=env['OS_USER_DOMAIN_ID'],
                               project_name=env['OS_PROJECT_NAME'],
                               project_domain_name=env['OS_PROJECT_DOMAIN_ID'])

            sess = session.Session(auth=auth)
            keystone = client.Client(session=sess)

            return keystone

        # No environment variables found
        except Exception:
            sys.exit()


    # find_secgroup: Given a project id, returns its
    # default security group ID.
    def find_secgroup(self, neutron, project_id):
        secgroups = neutron.list_security_groups()
        for sec in secgroups['security_groups']:
            if sec['tenant_id'] == project_id:
                return sec['id']



    def nova_auth(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
                                        username=env['OS_USERNAME'],
                                        password=env['OS_PASSWORD'],
                                        project_name=env['OS_PROJECT_NAME'],
                                        project_domain_name=env['OS_PROJECT_DOMAIN_ID'],
                                        user_domain_name=env['OS_USER_DOMAIN_ID'])

        sess = session.Session(auth=auth)
        nova = vclient.Client(2, session=sess)

        return nova


    # neutron_auth: Connects with neutrons auth server and
    # returns a client object.
    def neutron_auth(self, user):
        neutron = nclient.Client(username=user.name,
                                 password=user.password,
                                 tenant_name=user.project_name,
                                 auth_url='http://controller:5000/v2.0/')
        return neutron


    # register_user: Method responsible for creating all basic
    # keystone setup: user, project and role setup.
    def register_user(self, user):

        keystone = self.keystone_auth()
        nova     = self.nova_auth()

        p = keystone.projects.create(name    = user.project_name,
                                     domain  = user.domain,
                                     enabled = True)

        u = keystone.users.create(name             = user.name,
                                  default_project  = p,
                                  domain           = user.domain,
                                  password         = user.password,
                                  email            = user.email,
                                  enabled          = True)

        # update tenant_id and user_id
        self.network['tenant_id'] = p.id
        user.user_id    = u.id
        user.project_id = p.id

        # set projects quota
        self.update_project_quota(p.id, nova)

        # add user role to project
        os.system("openstack role add --project %s --user %s user" %(p.id, u.id))


    # update_project_quota: Updates a given project's quota
    # by using quota dict
    def update_project_quota(self, tenant_id, nova):
        nova.quotas.update(tenant_id,
                           intances     = var.quota['instances'],
                           cores        = var.quota['cores'],
                           ram          = var.quota['ram'],
                           floating_ips = var.quota['floating_ips'])

    # create_network: Method responsible for setting up all
    # necessary steps for a basic project network environment.
    def create_network(self, user):

        # Authenticate
        neutron = self.neutron_auth(user)

        # Create network
        ntwk = neutron.create_network({'network':var.network})

        # Create subnet
        self.subnet['network_id'] = ntwk['network']['id']
        sbnt = neutron.create_subnet({'subnet':self.subnet})

        # Create router
        rtr = neutron.create_router({'router':
                           {'name':'router',
                            'tenant_id': self.network['tenant_id']}})

        # Add ext-net gateway to router
        neutron.add_gateway_router(rtr['router']['id'],
                                   {'network_id': env['OS_EXT_NET']})

        # Add created subnet interface to router
        neutron.add_interface_router(rtr['router']['id'],
                                    {'subnet_id': sbnt['subnet']['id']})

        # Find ID of security_group based on project_id
        sc_grp = self.find_secgroup(neutron, self.network['tenant_id'])

        # Create SSH rule
        neutron.create_security_group_rule(
               {'security_group_rule': {'direction':'ingress',
                                        'port_range_min':'22',
                                        'port_range_max':'22',
                                        'ethertype':'IPv4',
                                        'protocol':'tcp',
                                        'security_group_id': sc_grp}})
        # Create ping rule
        neutron.create_security_group_rule(
               {'security_group_rule': {'direction':'ingress',
                                        'ethertype':'IPv4',
                                        'protocol':'icmp',
                                        'security_group_id': sc_grp}})


    def update_user(self, d):
        keystone = self.keystone_auth()

        if 'name' in d:
            keystone.users.update(d['user_id'], name=d['name'])
        if 'email' in d:
            keystone.users.update(d['user_id'], email=d['email'])
        if 'password' in d:
            keystone.users.update(d['user_id'], password=d['password'])
        if 'project_name' in d:
            keystone.projects.update(d['project_id'], name=d['project_name'])
        if 'description' in d:
            keystone.projects.update(d['project_id'], description=d['description'])
        if 'enabled' in d:
            keystone.projects.update(d['project_id'], enabled=d['enabled'])
            keystone.users.update(d['user_id'], enabled=d['enabled'])

    def get_user(self, user = None):
        keystone = self.keystone_auth()

        if user is None:
            return keystone.users.list()
        return keystone.users.get(user.user_id)

    def get_project(self, user):
        keystone = self.keystone_auth()
        return keystone.projects.get(user.project_id)
