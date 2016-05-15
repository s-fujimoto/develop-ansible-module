#!/usr/bin/env python

from ansible.module_utils.basic import *

class Linux(object):
    platform = 'Generic'
    distribution = None

    def __new__(cls, *args, **kwargs):
        return load_platform_subclass(Linux, args, kwargs)

    def hello(self):
        return 'I am %s' % (self.distribution if self.distribution else self.platform)

class AmazonLinux(Linux):
    platform = 'Linux'
    distribution = 'Amazon'

class CentOS6(Linux):
    platform = 'Linux'
    distribution = 'Centos'

class CentOS7(Linux):
    platform = 'Linux'
    distribution = 'Centos linux'

class Ubuntu(Linux):
    platform = 'Linux'
    distribution = 'Ubuntu'

class OSX(Linux):
    platform = 'Darwin'
    distribution = None

def main():
    module = AnsibleModule({})
    linux = Linux()
    module.exit_json(msg=linux.hello())

main()
