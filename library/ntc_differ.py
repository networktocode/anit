import os
import difflib
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            pre_change=dict(required=True),
            post_change=dict(required=True),
            dest=dict(required=True)
        )
    )

    with open(module.params['pre_change']) as f:
        pre_change = f.readlines()
    with open(module.params['post_change']) as f:
        post_change = f.readlines()

    diff = list(
        difflib.unified_diff(
            pre_change,
            post_change,
            fromfile=module.params['pre_change'],
            tofile=module.params['post_change']
        )
    )

    with open(module.params['dest'], 'w') as f:
        for line in diff:
            f.write(line)

    module.exit_json(
        changed=False,
        diff_output=''.join(diff),
        dest=os.path.abspath(module.params['dest'])
    )

if __name__ == '__main__':
    main()