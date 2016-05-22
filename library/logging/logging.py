#!/usr/bin/env python
from ansible.module_utils.basic import *

module = AnsibleModule({})
module.log("info log")
module.debug("debug log")

module.exit_json()
