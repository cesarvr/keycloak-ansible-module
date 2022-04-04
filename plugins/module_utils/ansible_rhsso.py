# testing
from .ansible_state import AnsibleState
from kcapi.ie import AuthenticationFlowsImporter
from kcapi import Keycloak
import json, os


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
    def __init__(self, resource, body):
        self.body = body
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


class ActionRealm(Action):
    def remove(self, key):
        self.resource.remove(self.body[key])


def retrieve_json_files_only(doc):
    return '.json' in doc


def get_json_docs_from_folder(folder):
    ret_list = []
    docs = os.listdir(folder)
    json_file_names = filter(retrieve_json_files_only, docs)
    for file in json_file_names:
        ret_list.append(folder + file)

    return ret_list


def make_action_objects(file_location, params):
    params['payload'] = file_location
    return AnsibleAction(params)


class LoadResourcesFromFolder(AnsibleState):
    def __init__(self, params):
        if params['folder'][-1] != '/':
            params['folder'] += '/'

        files = get_json_docs_from_folder(params['folder'])

        self.actions = list(map(lambda file: make_action_objects(file, params), files))

    def present(self):
        for action in self.actions:
            action.present()

    def absent(self):
        for action in self.actions:
            action.absent()


class AnsibleAction(AnsibleState):
    def __init__(self, params):
        self.key = params['id']
        self.realm = params['realm']
        self.name = params['name']
        self.body = readFromJSON(params['payload'])
        self.identifier = self.body[self.key]
        self.action_object = None
        self.params = params

    def configure(self):
        realm = self.realm
        params = self.params

        if self.name == 'realm':
            resource = Resource.createAdmin(params, self.name)
            self.action_object = ActionRealm
        else:
            self.action_object = Action
            resource = Resource.createWithName(params, self.name, realm)

        self.resource = resource
        super().__init__()

    def present(self):
        self.configure()
        action = self.action_object(self.resource, self.body)
        return action.create(self.key)

    def absent(self):
        self.configure()
        action = self.action_object(self.resource, self.body)
        return action.remove(self.key)


class GroupsAction(AnsibleState):
    def __init__(self, params, fileName):
        self.groupName = params['name']
        realm = params['realm']
        self.userKey = 'username' if not params['user_id'] else params['user_id']
        self.usersAPI = Resource.createWithName(params, 'users', realm)
        self.fileName = fileName
        super().__init__()

    def present(self):
        fileName = self.fileName
        userBody = readFromJSON(fileName)
        userFieldValue = userBody[self.userKey]

        usr = {"key": self.userKey, "value": userFieldValue}
        gpr = {"key": "name", "value": self.groupName}

        return self.usersAPI.joinGroup(usr, gpr).isOk()

    def absent(self):
        fileName = self.fileName
        userBody = readFromJSON(fileName)
        userFieldValue = userBody[self.userKey]

        usr = {"key": self.userKey, "value": userFieldValue}
        gpr = {"key": "name", "value": self.groupName}

        return self.usersAPI.leaveGroup(usr, gpr)


class RolesToGroupAction(AnsibleState):
    def __init__(self, params, roles):
        self.groupName = params['name']
        self.roles = roles
        self.realm = params['realm']
        self.params = params

        super().__init__()

    def present(self):
        roles = self.roles
        group = {"key": "name", "value": self.groupName}
        groups = Resource.createWithName(self.params, 'groups', self.realm)
        return groups.realmRoles(group).add(roles)

    def absent(self):
        roles = self.roles
        group = {"key": "name", "value": self.groupName}
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

    def present(self):
        self.flowAPI.create(self.parent).isOk()
        return self.publisher.publish(self.parent, self.payload)

    def absent(self):
        alias = self.parent['alias']
        exist = self.flowAPI.existByKV('alias', self.parent['alias'])

        if exist:
            return self.flowAPI.removeFirstByKV('alias', alias)
        else:
            return False
