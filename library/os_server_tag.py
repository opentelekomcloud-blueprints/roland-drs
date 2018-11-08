#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2018, Artem Goncharov <artem.goncharov@gmail.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_server_tag
short_description: Manage server tags
extends_documentation_fragment: openstack
version_added: "2.8"
author: "Artem Goncharov (gtema)"
description:
    - set or delete tag from the Nova server
options:
   server:
      description:
        - Name or id of the server
      required: true
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
   tag:
     description:
       - tag name
     required: true
requirements:
    - "python >= 2.7"
    - "openstacksdk"
'''
EXAMPLES = '''
---
- name: set the tag on the instance
  ignore_errors: True
  os_server_tag:
    server: "{{ server_name }}"
    state: present
    name: __type_baremetal
'''

RETURN = '''
None
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module
from ansible.module_utils._text import to_native


def main():

    argument_spec = openstack_full_argument_spec(
        server=dict(required=True),
        state=dict(default='present', choices=['absent', 'present']),
        tag=dict(required=True),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    server = module.params['server']
    state = module.params['state']
    tag = module.params['tag']

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        server = cloud.get_server(server)
        # Unless this is implemented in openstacksdk do direct requests
        if server:
            url = ('/servers/%(server)s/tags/%(tag)s'
                   % {
                        'server': server.id,
                        'tag': tag
                     }
                   )
            if state == 'present':
                cloud.compute.put(url, microversion='2.26')
            else:
                cloud.compute.delete(url, microversion='2.26')
            module.exit_json(changed=True,
                             server=server.id,
                             )
        module.exit_json(changed=False)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()
