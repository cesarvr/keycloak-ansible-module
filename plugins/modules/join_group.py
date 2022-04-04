from ansible.module_utils.basic import *

from ..module_utils.ansible_rhsso import GroupsAction

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
        "user_id": {"required": False, "type": "str" },
        "folder": {"required": True, "type": "str"},
        "token":{"required": True, "type": "str" },
        "endpoint":{"required": True, "type": "str" },
        "realm":{"required": True, "type": "str" },
        
        "state": GroupsAction.getAvailableStates() 
    }

def main():
    module = AnsibleModule(argument_spec=fields, )

    folder = module.params['folder']
    choice = module.params['state']
    jsonFileList = get_json_docs_from_folder(folder)  

    changes = 0

    for fileName in jsonFileList:
        groups = GroupsAction(params=module.params, fileName=fileName)
        changes += 1 if groups.run(choice) else 0

    module.exit_json(changed=changes>0, result={'state': True})

if __name__ == '__main__':
    main()
