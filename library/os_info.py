#!/usr/bin/env python
from ansible.module_utils.basic import *
module = AnsibleModule({})
module.exit_json(
    platform=get_platform(),
    distribution=get_distribution(),
    version=get_distribution_version()
)
