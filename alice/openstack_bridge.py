# from neutronclient.v2_0 import client as nclient
# from keystoneauth1.identity import v3
# from keystoneauth1 import session
# from keystoneclient.v3 import client
from os import environ as env
from view import View
import sys
import os



class OpenstackBridge:

    v = None

    user_variables = {'username'    : None,
                      'email'       : None,
                      'enabled'     : True,
                      'domain'      : 'default',
                      'project_name': 'project',
                      'password'    : 'pass',
                      'ext_net'     : '2f487de7-1695-475d-8345-4e6e681f699a'}

    network         = {'name'           : "Intranet",
                       'admin_state_up' : True,
                       'tenant_id'      : ''
                      }

    subnet          = {'name'           : "Subnet",
                       'ip_version'     : '4',
                       'cidr'           :'192.168.1.0/24',
                       'network_id'     : None,
                       'dns_nameservers': ['8.8.8.8'],
                       'enable_dhcp'    : True
                      }


    def __init__(self):
        self.v = View(self)

    def get(self, data):
        return self.user_variables[data]

    def get_var(self):
        return self.user_variables

    def set(self, data, content):
        self.user_variables[data] = content

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
            self.v.print_red(" :", "Admin? ", "- please, source openrc " +
                             "to get admin privileges.")
            sys.exit()


    # find_secgroup: Given a project id, returns its
    # default security group ID.
    def find_secgroup(self, neutron, project_id):
        secgroups = neutron.list_security_groups()
        for sec in secgroups['security_groups']:
            if sec['tenant_id'] == project_id:
                return sec['id']



    # TODO: Check if public keys path is valid
    def getPubKey(self, file_name):
        try:
            full_path = Path(file_name).expanduser()
            pub_key = open(str(full_path)).read()
        except Exception as e:
            print_red("\n :", "", "Invalid public key path (%s)" % file_name)
            print_red(" :", "", "Aborting...")
            sys.exit()


    # neutron_auth: Connects with neutrons auth server and
    # returns a client object.
    def neutron_auth(self):
        neutron = nclient.Client(username=self.get('username'),
                                 password=self.get('password'),
                                 tenant_name=self.get('project_name'),
                                 auth_url='http://controller:5000/v2.0/')
        return neutron


    # register_user: Method responsible for creating all basic
    # keystone setup: user, project and role setup.
    def register_user(self):

        # keystone = self.keystone_auth()

        # p = keystone.projects.create(name    = self.get('project_name'),
        #                              domain  = self.get('domain'),
        #                              enabled = self.get('enabled'))
        #
        # u = keystone.users.create(name             = self.get('username'),
        #                           default_project  = p,
        #                           domain           = self.get('domain'),
        #                           password         = self.get('password'),
        #                           email            = self.get('email'),
        #                           enabled          = self.get('enabled'))

        # self.network['tenant_id'] = p.id
        # os.system("openstack role add --project %s --user %s user" %(p.id, u.id))
        return 0

    # create_network: Method responsible for setting up all
    # necessary steps for a basic project network environment.
    def create_network(self):
        return 0
        # # Authenticate
        # neutron = self.neutron_auth()
        #
        # # Create network
        # ntwk = neutron.create_network({'network':self.network})
        #
        # # Create subnet
        # self.subnet['network_id'] = ntwk['network']['id']
        # sbnt = neutron.create_subnet({'subnet':self.subnet})
        #
        # # Create router
        # rtr = neutron.create_router({'router':
        #                    {'name':'router',
        #                     'tenant_id': self.network['tenant_id']}})
        #
        # # Add ext-net gateway to router
        # neutron.add_gateway_router(rtr['router']['id'],
        #                            {'network_id': self.get('ext_net')})
        #
        # # Add created subnet interface to router
        # neutron.add_interface_router(rtr['router']['id'],
        #                             {'subnet_id': sbnt['subnet']['id']})
        #
        # # Find ID of security_group based on project_id
        # sc_grp = self.find_secgroup(neutron, self.network['tenant_id'])
        #
        # # Create SSH rule
        # neutron.create_security_group_rule(
        #        {'security_group_rule': {'direction':'ingress',
        #                                 'port_range_min':'22',
        #                                 'port_range_max':'22',
        #                                 'ethertype':'IPv4',
        #                                 'protocol':'tcp',
        #                                 'security_group_id': sc_grp}})
        # # Create ping rule
        # neutron.create_security_group_rule(
        #        {'security_group_rule': {'direction':'ingress',
        #                                 'ethertype':'IPv4',
        #                                 'protocol':'icmp',
        #                                 'security_group_id': sc_grp}})
