# testing
import os, sys

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
        if self.__exist(key): 
            return False
        else:
            return self.resource.create(self.body).isOk()

class AnsibleState: 
    @staticmethod
    def getAvailableStates():
        return {
            "default": "present", 
            "choices": ['present', 'absent'],  
            "type": 'str' 
        }

    def __init__(self):
        self.choices = {'present': self.present, 'absent': self.absent}

    def run(self, state_choice, filename):
        self.choices[state_choice](filename)

    def present(self): 
        return True

    def absent(self): 
        return True

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
       self.userKey = params['user_id']
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


class RolesToGroup(AnsibleState): 
    def __init__(self, params):
        self.groupName = params['name']

        realm = params['realm']
        self.groups = Resource.createWithName(params, 'groups', realm)
       
        super().__init__()

    def present(self, roles): 
        group = {"key":"name", "value": self.groupName}
        return self.groups.addRealmRoles(group, roles)
        
    def absent(self, roles): 
        group = {"key":"name", "value": self.groupName}
        return self.groups.removeRealmRoles(group, roles)
     
        
        


