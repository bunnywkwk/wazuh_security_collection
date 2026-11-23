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
DEFS = "# comment\nUID_MIN                  1000\nUID_MAX                 60000\nPASS_MAX_DAYS 99999\n"
SHELLS = ['/sbin/nologin', '/usr/sbin/nologin', '/bin/false', '/usr/bin/false']

got = sort_accounts([[PASSWD, DEFS]], SHELLS)
assert got['standard'] == ['frqadmin', 'svc_report'], got
assert got['service'] == ['daemon', 'nginx', 'nobody', 'olduser', 'svc_backup'], got
assert 'svc_report' in got['standard'], got
# A name pattern moves a normal-looking account to service
got = sort_accounts([[PASSWD, DEFS]], SHELLS, ['^svc_'])
assert got['standard'] == ['frqadmin'], got
assert 'svc_report' in got['service'], got
# UID_MIN differs per host: olduser is standard on the second host, so it is in both lists
got = sort_accounts([[PASSWD, DEFS], [PASSWD, "UID_MIN 500\n"]], SHELLS)
assert got['standard'] == ['frqadmin', 'olduser', 'svc_report'], got
assert 'olduser' in got['service'], got
print('ok')
