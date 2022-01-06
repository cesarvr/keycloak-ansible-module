from __future__ import absolute_import
import time


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

    def run(self, choice, filename):
        if choice == 'present':
            self.absent(filename)

            return self.present(filename)

        if choice == 'absent':
            return self.absent(filename)

    def present(self): 
        return True

    def absent(self): 
        return True

