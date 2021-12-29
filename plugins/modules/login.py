from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import *

from kcapi import OpenID 

fields = {
    "username":{"required": True, "type": "str" },
    "password":{"required": True, "type": "str", "no_log": True },
    "endpoint":{"required": True, "type": "str" },
}

def main():
    module = AnsibleModule(argument_spec=fields)

    username = module.params['username']
    password = module.params['password']
    endpoint = module.params['endpoint']

    token = OpenID.createAdminClient(username, password).getToken(endpoint)


    module.exit_json(changed=False, result={'state': True, 'token': token})

if __name__ == '__main__':
    main()
