from ansible.module_utils.basic import *
from ..module_utils.ansible_rhsso import RolesToGroupAction

fields = {
        "group": {"required": True, "type": "str" },
        "roles": {"required": True, "type": "list" },
        "token":{"required": True, "type": "str" },
        "endpoint":{"required": True, "type": "str" },
        "realm":{"required": True, "type": "str" },
        
        "state": RolesToGroupAction.getAvailableStates() 
    }

def main():
    module = AnsibleModule(argument_spec=fields)
    choice = module.params['state']
    roles = module.params['roles'] 
    module.params['name'] = module.params['group']

    group = RolesToGroupAction(params = module.params)
    resp = group.run(choice, roles) 

    module.exit_json(changed=resp.isOk(), result={'state': True, 'list': roles })

if __name__ == '__main__':
    main()
