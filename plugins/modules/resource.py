from __future__ import absolute_import
from ansible.module_utils.basic import *

from ..module_utils.ansible_rhsso import AnsibleAction


DOCUMENTATION = r"""
module: resource
author:
  - "cesarv01@yahoo.com"
version_added: '1.0.0'
short_description: Add/Remove resources configuration to Keycloak (or Red Hat Single Sign-On). 
notes: []
description:
  - Add/Remove resources configuration to Keycloak (or Red Hat Single Sign-On). Where resource can be any configuration (clients, federation component, users, groups, etc.) 
options:
  name:
    description:
      - Add/Remove resources configuration to Keycloak (or Red Hat Single Sign-On). 
    required: True
    type: str
  id:
    description:
      - The field that uniquely identifies the Resource on the Keycloak server. (for example: the field ``name`` for groups)
    required: True
    type: str
  token:
    description:
      - A valid OpenID token with permissions to perform the desired operation. 
    required: True
    type: str
  endpoint:
    description:
      - A valid URL pointing to Keycloak. (example: https://mykeycloak.org or https://100.1.2.3:8443)
    required: True
    type: str
  payloads: 
    description: 
      - The content of a JSON file with the description of the resource.
    required: True
    type: str
  realm: 
    description: 
      - If the resource need to exist in a specific realm other than Master, then we need to provide the Realm name. 
  state:
    description:
      - I(absent) - Removes the resource from the server.
      - I(present) - Publish the desired resource in the server. 
    type: str
    default: present
    choices:
      - absent
      - present
"""

EXAMPLES = r"""
- name: Publish a client in realm *heroes*
  keycloak.robot.resource: 
    name: clients 
    id: clientId
    realm: 'heroes'
    token: '<your-token-goes-here>'
    endpoint: 'https://my_keycloak_server' 
    payloads: files/clients/marvel.json
    state: present   

- name: Creates a realm 
  keycloak.robot.resource: 
    name: realm 
    id: 'id'
    token: '<your-token-goes-here>'
    endpoint: 'https://my_keycloak_server' 
    payloads: files/realm.json
    state: present    


- name: Removes a realm 
  keycloak.robot.resource: 
    name: realm 
    id: 'id'
    token: '<your-token-goes-here>'
    endpoint: 'https://my_keycloak_server' 
    payloads: files/realm.json
    state: absent    
"""

RETURN = r""" """

fields = {
        "name": {"required": True, "type": "str" },
        "payload": {"required": True, "type": "str"},
        "token": {"required": True, "type": "str" },
        "endpoint": {"required": True, "type": "str" },
        "id": {"required": True, "type": "str" },
        "realm":{"required": False, "type": "str" },

        "state": AnsibleAction.getAvailableStates() 
}

def main():

    module = AnsibleModule(argument_spec=fields)
    ansibleAction = AnsibleAction(params=module.params)

    state_choice = module.params['state']
    state = ansibleAction.run(state_choice)
    module.exit_json(changed=state, result={'state': True, 'name': ansibleAction.identifier})

if __name__ == '__main__':
    main()
