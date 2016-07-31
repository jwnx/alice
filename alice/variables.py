yes = set(['yes', 'y', 'ye'])
no = set(['no', 'n'])
edit = set(['e', 'edit'])
DOT = ' :'
ARW = ' >'

MSG = {'CHECK' : '\n : Checking missing variables.. ',
       'ADD'   : '\n : Do you want to add the above user? (y/n) ',
       'CERROR': 'Wrong input',
       'ABORT' : 'Aborting...',
       'REGK'  : 'Registering user in keystone...',
       'REGN'  : 'Creating base network settings...'}


user           = {'username'        : None,
                  'email'           : None,
                  'enabled'         : True,
                  'domain'          : 'default',
                  'project_name'    : 'project',
                  'password'        : 'pass',
                  'ext_net'         : ''}

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

quota           = {'instances'      : 4,
                   'cores'          : 8,
                   'ram'            : 4096,
                   'floating_ips'   : 4
                  }
