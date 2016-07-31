user           = {'username'        : None,
                  'email'           : None,
                  'enabled'         : True,
                  'domain'          : 'default',
                  'project_name'    : 'project',
                  'password'        : 'pass',
                  'ext_net'         : '',
                  'user_id'         : ''}

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
