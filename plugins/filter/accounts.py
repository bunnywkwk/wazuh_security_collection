"""Sort the local accounts of hosts into service and standard accounts, for the SEC-TH-001 / 002 CDB lists."""
import re


def sort_host(passwd, login_defs, nologin_shells, service_patterns):
    """passwd: getent_passwd from ansible.builtin.getent ({name: [pw, uid, gid, gecos, home, shell]}).
    login_defs: text of /etc/login.defs. nologin_shells: shells that cannot log in.
    service_patterns: regexes of names that are service accounts whatever their UID and shell (^svc_).

    standard = UID_MIN to UID_MAX with a login shell; service = every other account except root (SEC-TH-003).
    """
    defs = {}
    for line in login_defs.splitlines():
        words = line.split()
        if len(words) >= 2 and not words[0].startswith('#'):
            defs[words[0]] = words[1]
    uid_min = int(defs.get('UID_MIN', 1000))
    uid_max = int(defs.get('UID_MAX', 60000))

    service, standard = [], []
    for name, fields in passwd.items():
        uid, shell = int(fields[1]), fields[5]
        if uid == 0:
            continue
        named_service = any(re.search(p, name) for p in service_patterns)
        if uid_min <= uid <= uid_max and shell not in nologin_shells and not named_service:
            standard.append(name)
        else:
            service.append(name)
    return service, standard


def sort_accounts(hosts, nologin_shells, service_patterns=()):
    """hosts: one [passwd, login_defs] pair per host. Returns the union over all hosts.
    A name that is a service account on one host and standard on another lands in both lists."""
    service, standard = set(), set()
    for passwd, login_defs in hosts:
        host_service, host_standard = sort_host(passwd, login_defs, nologin_shells, service_patterns)
        service.update(host_service)
        standard.update(host_standard)
    return {'service': sorted(service), 'standard': sorted(standard)}


class FilterModule:
    def filters(self):
        return {'sort_accounts': sort_accounts}
