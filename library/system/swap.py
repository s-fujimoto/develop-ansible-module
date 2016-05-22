#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: swap
author: Shinji Fujimoto
short_description: Create swap file
requirements: None
description:
    - Set swapfile and
    - Currently implemented on RedHat, CentOS, Amazon Linux.
options:
    size:
        required: False
        description:
            - Size of swap
    filepath:
        required: False
        description:
            - Filepath of swap
'''

EXAMPLES = '''
- swap: size=1G filepath=/swap.img
'''

from distutils.version import LooseVersion
from ansible.module_utils.basic import *
import os
import re


def _check_version(min=None, max=None):
    version = get_distribution_version()
    if not version or \
       (isinstance(min, str) and LooseVersion(version) < LooseVersion(min)) or \
       (isinstance(max, str) and LooseVersion(version) >= LooseVersion(max)):
        return False
    return True


#----- Processor Class
class UnimplementedSwap(object):

    def __init__(self, module):
        distribution = get_distribution()
        module.fail_json(
            msg='swap module cannot be used on %s' % (distribution if distribution else get_platform())
        )


class GenericSwap(object):

    CREATE_SWAPFILE_CMD = '/usr/bin/fallocate'
    MAKE_SWAP_CMD = '/sbin/mkswap'
    FILE_CMD = '/usr/bin/file'
    SWAPON_CMD = '/sbin/swapon'
    FSTAB_PATH = '/etc/fstab'

    def __init__(self, module):
        self.module = module
        self.size = module.params['size']
        self.filepath = module.params['filepath']

        if not self.size:
            self.size = self._get_memsize()

    def create_swapfile(self):
        if os.path.exists(self.filepath):
            return False

        cmd = [self.CREATE_SWAPFILE_CMD, '-l', self.size, self.filepath]
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='%s command failed. rc=%d, out=%s, err=%s' % (cmd[0], rc, out, err))

        os.chmod(self.filepath, 0600)

        return True

    def make_swap(self):
        cmd = [self.FILE_CMD, self.filepath]
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='%s command failed. rc=%d, out=%s, err=%s' % (cmd[0], rc, out, err))

        if 'swap file' in out:
            return False

        cmd = [self.MAKE_SWAP_CMD, self.filepath]
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='%s command failed. rc=%d, out=%s, err=%s' % (cmd[0], rc, out, err))

        return True

    def set_fstab(self):
        with open(self.FSTAB_PATH, 'a+') as f:
            if filter(lambda line: line.startswith(self.filepath), f.readlines()):
                return False

            f.write(self.filepath + ' swap swap defaults 0 0\n')

    def mount_swap(self):
        with open('/proc/swaps') as f:
            if filter(lambda line: line.startswith(self.filepath), f.readlines()):
                return False

        cmd = [self.SWAPON_CMD, self.filepath]
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='%s command failed. rc=%d, out=%s, err=%s' % (cmd[0], rc, out, err))

        return True

    def _get_memsize(self):
        with open('/proc/meminfo') as f:
            for line in filter(lambda line: line.startswith('MemTotal:'), f.readlines()):
                return re.split('\s+', line)[1] + 'k'


class CentOS5Swap(GenericSwap):

    CREATE_SWAPFILE_CMD = '/bin/dd'
    BLOCK_SIZE = 1024 * 1024

    def create_swapfile(self):
        if os.path.exists(self.filepath):
            return False

        print self.module.log(self.size)

        if self.size.endswith(('k', 'K')):
            self.size = float(self.size[:-1]) * 1024
        elif self.size.endswith(('m', 'M')):
            self.size = float(self.size[:-1]) * 1024 * 1024
        elif self.size.endswith(('g', 'G')):
            self.size = float(self.size[:-1]) * 1024 * 1024 * 1024
        else:
            self.size = float(self.size)

        count = int(self.size / self.BLOCK_SIZE)

        cmd = [self.CREATE_SWAPFILE_CMD, 'if=/dev/zero', 'of=%s' % self.filepath, 'bs=%d' % self.BLOCK_SIZE, 'count=%d' % count]

        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg='%s command failed. rc=%d, out=%s, err=%s' % (cmd[0], rc, out, err))

        os.chmod(self.filepath, 0600)

        return True


#----- Factory Class
class Creator(object):
    platform = 'Generic'
    distribution = None
    swap_class = UnimplementedSwap

    @classmethod
    def createSwap(cls, module):
        return load_platform_subclass(cls).swap_class(module)


class CentosCreator(Creator):
    platform = 'Linux'
    distribution = 'Centos'
    if _check_version(min='6', max='7'):
        swap_class = GenericSwap
    elif _check_version(min='5', max='6'):
        swap_class = CentOS5Swap


class CentosLinuxCreator(Creator):
    platform = 'Linux'
    distribution = 'Centos linux'
    swap_class = CentOS5Swap


class AmazonLinuxCreator(Creator):
    platform = 'Linux'
    distribution = 'Amazon'
    swap_class = GenericSwap


class UbuntuCreator(Creator):
    platform = 'Linux'
    distribution = 'Ubuntu'
    swap_class = GenericSwap


def main():
    module = AnsibleModule(
        argument_spec = dict(
            size=dict(required=False, type='str'),
            filepath=dict(required=True, type='str')
        )
    )

    swap = Creator.createSwap(module=module)

    changed = False

    if swap.create_swapfile():
        changed = True
    if swap.make_swap():
        changed = True
    if swap.set_fstab():
        changed = True
    if swap.mount_swap():
        changed = True

    module.exit_json(changed=changed)

main()
