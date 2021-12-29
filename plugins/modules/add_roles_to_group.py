from ansible.module_utils.basic import *

# testing
import os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath("./kc"))
sys.path.append(os.path.dirname(SCRIPT_DIR))
#TODO remove this
sys.path.append(os.path.dirname('/Users/cesar/Workarea/rh/dsv/ansible_plugin/library/rhsso_api'))

#SCRIPT_DIR = os.path.dirname(os.path.abspath("./kc"))
#sys.path.append(os.path.dirname(SCRIPT_DIR))

from rhsso_api import RolesToGroup

def retrieve_json_files_only(doc): 
    return '.json' in doc

def get_json_docs_from_folder(folder):
    ret_list = []
    docs = os.listdir(folder) 
    json_fnames = filter(retrieve_json_files_only, docs)
    for doc in json_fnames: 
        ret_list.append(folder + doc)

    return ret_list
        
   
fields = {
        "group": {"required": True, "type": "str" },
        "roles": {"required": True, "type": "list" },
        "token":{"required": True, "type": "str" },
        "endpoint":{"required": True, "type": "str" },
        "realm":{"required": True, "type": "str" },
        
        "state": RolesToGroup.getAvailableStates() 
    }

def main():
    module = AnsibleModule(argument_spec=fields)
    choice = module.params['state']
    roles = module.params['roles'] 
    module.params['name'] = module.params['group']

    group = RolesToGroup(params = module.params)
    change_state = group.run(choice, roles) 

    module.exit_json(changed=change_state, result={'state': True, 'list': roles })

if __name__ == '__main__':
    main()
