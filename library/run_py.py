#!/usr/bin/env python
from ansible.module_utils.basic import *
module = AnsibleModule({})
rc, stdout, stderr = module.run_command("mkdir -v /ZZZ/test_dir")
module.exit_json(
    changed=True,
    rc=rc,
    stdout=stdout,
    stderr=stderr
)
