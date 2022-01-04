from __future__ import absolute_import

''' 
Class in charge of encapsulating Ansible related things.

'''
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

