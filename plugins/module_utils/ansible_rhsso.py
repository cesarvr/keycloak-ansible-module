# testing
import os, sys

from .ansible_state import AnsibleState
from kcapi.ie import AuthenticationFlowsImporter   
from kcapi import Keycloak
import json

def readFromJSON(filename):
    with open(filename) as json_file:
        return json.load(json_file)

class Resource: 
    @staticmethod
    def __buildKeycloak(params): 
        token = params['token']
        endpoint = params['endpoint']
        return Keycloak(token, endpoint)

    @staticmethod
    def createWithName(params, name, realm):
        keycloak = Resource.__buildKeycloak(params)
        return keycloak.build(name, realm)

    @staticmethod
    def createAdmin(params, name):
        keycloak = Resource.__buildKeycloak(params)
        return keycloak.admin()

class Action: 
    def __init__(self, resource, fileName):
        self.body = readFromJSON(fileName)
        self.resource = resource

    def __exist(self, key): 
        value = self.body[key]
        return self.resource.existByKV(key, value) 

    def remove(self, key):
        if not self.__exist(key):
           return False
        else:
           value = self.body[key]
           return self.resource.removeFirstByKV(key, value)

    def create(self, key):
        return self.resource.create(self.body).isOk()

class AnsibleAction(AnsibleState): 
    def __init__(self, params):
        self.key = params['id'] 
        realm = params['realm'] 
        name = params['name'] 

        if name == 'realm' and not realm: 
            resource = Resource.createAdmin(params, name)
        else:
            resource = Resource.createWithName(params, name, realm)
            
        self.resource = resource 
        super().__init__()

    def present(self, filename): 
        action = Action(self.resource, filename) 
        return action.create(self.key)

    def absent(self, filename): 
        action = Action(self.resource, filename) 
        return action.remove(self.key)

class GroupsAction(AnsibleState): 
    def __init__(self, params):
       self.groupName = params['name']   
       realm = params['realm'] 
       self.userKey = 'username' if not params['user_id'] else params['user_id']
       self.usersAPI = Resource.createWithName(params, 'users', realm)

       super().__init__()
       
    def present(self, filename): 
        userBody = readFromJSON(filename)
        userFieldValue = userBody[self.userKey] 

        usr = { "key": self.userKey, "value": userFieldValue }
        gpr = { "key": "name", "value": self.groupName }

        return self.usersAPI.joinGroup(usr, gpr).isOk()

    def absent(self, filename): 
        userBody = readFromJSON(filename)
        userFieldValue = userBody[self.userKey] 

        usr = { "key": self.userKey, "value": userFieldValue }
        gpr = { "key": "name", "value": self.groupName }

        return self.usersAPI.leaveGroup(usr, gpr)


class RolesToGroupAction(AnsibleState): 
    def __init__(self, params):
        self.groupName = params['name']

        self.realm = params['realm']
        self.params = params
       
        super().__init__()

    def present(self, roles): 
        group = {"key":"name", "value": self.groupName}
        groups = Resource.createWithName(self.params, 'groups', self.realm)
        return groups.realmRoles(group).add(roles)
        
    def absent(self, roles): 
        group = {"key":"name", "value": self.groupName}
        groups = Resource.createWithName(self.params, 'groups', self.realm)
        return groups.realmRoles(group).remove(roles)
     
        
class AuthenticationFlowAction(AnsibleState): 
    def __init__(self, params):
        realm = params['realm']
        self.parent = readFromJSON(params['parent_flow'])
        self.payload = readFromJSON(params['payload']) 
        self.flowAPI = Resource.createWithName(params, 'authentication', realm)
        self.publisher = AuthenticationFlowsImporter(self.flowAPI)  
       
        super().__init__()

    def present(self, filename): 
        self.flowAPI.create(self.parent).isOk()
        return self.publisher.publish(self.parent, self.payload)
        
    def absent(self, filename): 
        alias = self.parent['alias']
        exist = self.flowAPI.existByKV('alias', self.parent['alias'])

        if exist:
            return self.flowAPI.removeFirstByKV('alias',alias)
        else:
            return False

     
        


