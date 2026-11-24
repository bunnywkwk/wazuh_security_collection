"""Run: python3 tests/unit/test_accounts.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'filter'))
from accounts import sort_accounts  # noqa: E402

PASSWD = {
    'root': ['x', '0', '0', 'root', '/root', '/bin/bash'],
    'daemon': ['x', '2', '2', 'daemon', '/sbin', '/usr/sbin/nologin'],
    'nginx': ['x', '980', '980', 'nginx', '/var/lib/nginx', '/sbin/nologin'],
    'frqadmin': ['x', '1000', '1000', '', '/home/frqadmin', '/bin/bash'],
    'svc_backup': ['x', '1001', '1001', '', '/home/svc_backup', '/usr/sbin/nologin'],
    'svc_report': ['x', '1002', '1002', '', '/home/svc_report', '/bin/bash'],
    'nobody': ['x', '65534', '65534', 'Kernel Overflow User', '/', '/usr/sbin/nologin'],
    'olduser': ['x', '500', '500', '', '/home/olduser', '/bin/bash'],
}
SHELLS = ['/sbin/nologin', '/usr/sbin/nologin', '/bin/false', '/usr/bin/false']

got = sort_accounts([PASSWD], 1000, 60000, SHELLS)
assert got['standard'] == ['frqadmin', 'svc_report'], got
assert got['service'] == ['daemon', 'nginx', 'nobody', 'olduser', 'svc_backup'], got
# A name pattern moves a normal-looking account to service
got = sort_accounts([PASSWD], 1000, 60000, SHELLS, ['^svc_'])
assert got['standard'] == ['frqadmin'], got
assert 'svc_report' in got['service'], got
# Two hosts: a name standard on one and service on the other is in both lists
other = {'olduser': ['x', '1500', '1500', '', '/home/olduser', '/bin/bash']}
got = sort_accounts([PASSWD, other], 1000, 60000, SHELLS)
assert 'olduser' in got['standard'] and 'olduser' in got['service'], got
print('ok')
