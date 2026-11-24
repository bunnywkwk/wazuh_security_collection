"""Sort the local accounts of hosts into service and standard accounts, for the SEC-TH-001 / 002 CDB lists."""
import re


def sort_accounts(passwds, uid_min, uid_max, nologin_shells, service_patterns=()):
    """passwds: one getent_passwd per host ({name: [pw, uid, gid, gecos, home, shell]}).
    standard = uid_min to uid_max, a login shell and no service name; service = every other account except root.
    Returns the union over all hosts: a name standard on one host and service on another is in both lists."""
    service, standard = set(), set()
    for passwd in passwds:
        for name, fields in passwd.items():
            uid, shell = int(fields[1]), fields[5]
            if uid == 0:
                continue   # root: SEC-TH-003
            named_service = any(re.search(p, name) for p in service_patterns)
            if uid_min <= uid <= uid_max and shell not in nologin_shells and not named_service:
                standard.add(name)
            else:
                service.add(name)
    return {'service': sorted(service), 'standard': sorted(standard)}


class FilterModule:
    def filters(self):
        return {'sort_accounts': sort_accounts}
