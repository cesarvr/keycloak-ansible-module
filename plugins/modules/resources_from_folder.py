
from __future__ import absolute_import
from ansible.module_utils.basic import *

from ..module_utils.ansible_rhsso import AnsibleAction

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
        "name": {"required": True, "type": "str" },
        "folder": {"required": True, "type": "str"},
        "token":{"required": True, "type": "str" },
        "endpoint":{"required": True, "type": "str" },
        "id":{"required": True, "type": "str" },
        "realm":{"required": False, "type": "str" },
    
        "state": AnsibleAction.getAvailableStates() 
        }

def main():
    module = AnsibleModule(argument_spec=fields)
    ansibleAction = AnsibleAction(params=module.params)

    choice = module.params['state']
    folder = module.params['folder']
    resource_file_list = get_json_docs_from_folder(folder)  

    changes = 0
    for file in resource_file_list:
        changes += 1 if ansibleAction.run(choice, file) else 0
    
    module.exit_json(changed=changes>0, result={'state': True})

if __name__ == '__main__':
    main()
