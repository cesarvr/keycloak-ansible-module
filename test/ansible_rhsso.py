import unittest, os
import json
from plugins.module_utils import AnsibleAction, LoadResourcesFromFolder
from kcapi import OpenID, Keycloak

USER = os.getenv('KC_USER')
PASSWORD = os.environ.get('KC_PASSWORD')
ENDPOINT = os.environ.get('KC_ENDPOINT')


def log_in():
    token = OpenID.createAdminClient(USER, PASSWORD).getToken(ENDPOINT)

    return token


def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()

    params = {'payload': fname, 'name': 'realm', 'id': 'realm', 'token': log_in(),
              'realm': None, 'endpoint': ENDPOINT}

    return {'document': file1, 'params': params}


class RHSSOModule(unittest.TestCase):

    def testing_when_required_present(self):
        realm_payload = './test/payloads/realm.json'
        obj = load_sample(realm_payload)
        document = obj['document']
        params = obj['params']

        ansible = AnsibleAction(params)

        # By testing this many times we make sure that we are able to delete/publish successfully, if this two actions are fail RHSSO will reject the object and the test will fail.
        for t in range(5):
            ansible.absent()
            ansible.present()

        realms = self.admin.findFirstByKV('realm', document['realm'])

        for key in document:
            if isinstance(document[key], list):
                self.assertEqual(document[key].sort(), realms[key].sort(),
                                 'The published object need to be consistent with the local copy.')
                continue

            self.assertEqual(document[key], realms[key],
                             'The published object need to be consistent with the local copy.')

    def testing_recursive_client_publisher(self):
        roles_folder = './test/payloads/roles'
        params = {'folder': roles_folder, 'name': 'roles', 'id': 'name', 'token': self.token,
                  'realm': self.REALM, 'endpoint': ENDPOINT}

        lrff = LoadResourcesFromFolder(params)

        lrff.absent()
        lrff.present()

        roles = self.kc.build('roles', self.REALM)

        role_documents = roles.all()
        self.assertEqual(len(role_documents), 4, 'Resources are not being published.')

        hero_role = roles.findFirstByKV('name', 'hero')
        self.assertIsNotNone(hero_role, 'Fail to publish the <hero> role into RH-SSO.')

        return 0

    @classmethod
    def setUpClass(self):
        self.REALM = 'heroes_copy'
        self.token = log_in()
        self.kc = Keycloak(self.token, ENDPOINT)
        self.admin = self.kc.admin()
        return True

    @classmethod
    def tearDownClass(self):
        # self.testbed.goodBye()
        return True


if __name__ == '__main__':
    unittest.main()
