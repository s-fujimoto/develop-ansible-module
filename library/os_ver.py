#!/usr/bin/env python

from distutils.version import LooseVersion
from ansible.module_utils.basic import *

class Strategy(object):
    version = 'none'

    def get_version(self):
        return 'My version is ' + self.version

class CentOS6Strategy(Strategy):
    version = '6'

class CentOS7Strategy(Strategy):
    version = '7'

class Ubuntu12Strategy(Strategy):
    version = '12'

class Ubuntu14Strategy(Strategy):
    version = '14'

class AmazonStrategy(Strategy):
    version = '2016.03'

class OSXStrategy(Strategy):
    version = 'Yosemite'

class Linux(object):
    platform = 'Generic'
    distribution = None
    strategy_class = Strategy

    def __new__(cls, *args, **kwargs):
        return load_platform_subclass(Linux, args, kwargs)

    def __init__(self):
        self.strategy = self.strategy_class()

    def hello(self):
        return 'I am %s. %s' % (self.distribution if self.distribution else self.platform, self.strategy.get_version())

class Amazon(Linux):
    platform = 'Linux'
    distribution = 'Amazon'
    strategy_class = AmazonStrategy

class CentOS6(Linux):
    platform = 'Linux'
    distribution = 'Centos'
    strategy_class = CentOS6Strategy

class CentOS7(Linux):
    platform = 'Linux'
    distribution = 'Centos linux'
    strategy_class = CentOS7Strategy

class Ubuntu(Linux):
    platform = 'Linux'
    distribution = 'Ubuntu'
    version = get_distribution_version()
    if version and LooseVersion('13') > LooseVersion(version) >= LooseVersion('12'):
        strategy_class = Ubuntu12Strategy
    elif version and LooseVersion('15') > LooseVersion(version) >= LooseVersion('14'):
        strategy_class = Ubuntu14Strategy

class OSX(Linux):
    platform = 'Darwin'
    distribution = None
    strategy_class = OSXStrategy

def main():
    module = AnsibleModule({})
    linux = Linux()
    module.exit_json(msg=linux.hello())

main()
