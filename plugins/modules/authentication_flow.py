from ansible.module_utils.basic import *

from ..module_utils.ansible_rhsso import AuthenticationFlowAction

fields = {
    "name": {"required": True, "type": "str"},
    "parent_flow": {"required": True, "type": "str"},
    "payload": {"required": True, "type": "str"},
    "token": {"required": True, "type": "str"},
    "endpoint": {"required": True, "type": "str"},
    "realm": {"required": True, "type": "str"},

    "state": AuthenticationFlowAction.getAvailableStates()
}


def main():
    module = AnsibleModule(argument_spec=fields)
    groups = AuthenticationFlowAction(params=module.params)
    choice = module.params['state']

    state = groups.run(choice)

    module.exit_json(changed=state, result={'state': True})


if __name__ == '__main__':
    main()
