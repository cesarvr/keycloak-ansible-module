
from __future__ import absolute_import
from ansible.module_utils.basic import *

from ..module_utils.ansible_rhsso import LoadResourcesFromFolder


fields = {
        "name": {"required": True, "type": "str" },
        "folder": {"required": True, "type": "str"},
        "token":{"required": True, "type": "str" },
        "endpoint":{"required": True, "type": "str" },
        "id":{"required": True, "type": "str" },
        "realm":{"required": False, "type": "str" },
    
        "state": LoadResourcesFromFolder.getAvailableStates()
        }

def main():
    module = AnsibleModule(argument_spec=fields)


    choice = module.params['state']
    folder = module.params['folder']

    from_folder_ansible_anction = LoadResourcesFromFolder(module.params)

    state = from_folder_ansible_anction.run(choice)
    
    module.exit_json(changed=state, result={'state': True})

if __name__ == '__main__':
    main()
