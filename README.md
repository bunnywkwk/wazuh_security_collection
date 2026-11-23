# bunnywkwk.wazuh_security

Ansible collection that deploys Wazuh detection for the RHEL security monitoring requirements, one security group at a time. No custom decoders: every rule builds on Wazuh's built-in decoders and rules.

- **manager** role: one rules file per requirement, `/var/ossec/etc/rules/<id>.xml` (`local_rules.xml` is never touched), and CDB lists in `/var/ossec/etc/lists/`, declared in `ossec.conf` (the only change there)
- **agent** role: what a host must log for the manager rules, one file per requirement (audit rules in `/etc/audit/rules.d/50-wazuh-<id>.rules`)

Groups: **Host Access**, **Privileged Activity**.

## Kinds of rules

| Kind | Template folder | When | Example |
|---|---|---|---|
| **record** | `record/` | Wazuh already detects it: a child rule that only adds the requirement ID | `rule.groups: sec_f_001` finds every successful login |
| **threshold** | `threshold/` | the requirement has a count in Annex B | SEC-TH-003: 3 / 5 failed root logins in 5 min |
| **overwrite** | `overwrite/` | a built-in rule changed in place | built-in 5763 set to level 0 |
| **list** | `list/` | names the rules look up (CDB list) | `etc/lists/service-accounts` for SEC-TH-001 |
| **alert** | `record/` | a single event that is itself the finding | SEC-F-019 direct root login |
| **audit rule** | agent `audit/` | the host must log it first | SEC-F-006 admin commands |
| **gap** | none | the host cannot see it: no rule, written down in the defaults file | SEC-F-016 BMC access |

## Layout

Same layout as the CIS roles: a task folder per group, a task file per requirement, templates split by kind.

```
roles/manager/defaults/main.yml                   group switch, one switch per requirement + its settings
roles/manager/tasks/main.yml                      imports each group when its switch is on
roles/manager/tasks/host_access/main.yml          imports each requirement file
roles/manager/tasks/host_access/sec_f_001.yml     "SEC-F-001 | RECORD | Record successful SSH logins"
roles/manager/templates/host_access/record/       sec_f_001, 002, 004, 016
roles/manager/templates/host_access/threshold/    sec_th_001 to 005
roles/manager/templates/host_access/overwrite/    silence_5763
roles/manager/templates/host_access/list/         accounts.j2 -> etc/lists/service-accounts, standard-accounts
roles/manager/templates/privileged_activity/record/      sec_f_005, 006, 018, 019
roles/manager/templates/privileged_activity/threshold/   sec_th_007
roles/agent/tasks/privileged_activity/sec_f_006.yml       "SEC-F-006 | AUDIT RULE | Record admin commands run as root"
roles/agent/templates/privileged_activity/audit/          sec_f_006.rules
plugins/filter/accounts.py                        filter sort_accounts
```

A counter must load before the thresholds that count it. The names keep that order (`sec_f_002.xml` before `sec_th_00N.xml`); if Wazuh ever loads them out of order, the `wazuh-analysisd -t` test fails before the restart.

## Host Access (100110-100129)

| Requirement | Kind | Rule IDs | Built on |
|---|---|---|---|
| SEC-F-001 successful login | record | 100110 | 5715 |
| SEC-F-002 failed login, existing account | record, also the counter for SEC-F-003 | 100111 | 5760 |
| SEC-F-002 failed login, account that does not exist | record only, not counted | 100124 | 5710 |
| SEC-F-003 brute force: SEC-TH-001 service accounts (read from the agents) | threshold | 100112 / 100113 | 100111 |
| SEC-TH-002 standard accounts (read from the agents) | threshold | 100114 / 100115 | 100111 |
| SEC-TH-003 privileged accounts | threshold | 100116 / 100117 | 100111 |
| SEC-TH-004 one source, any accounts | threshold | 100118 / 100119 | 100111 |
| SEC-TH-005 password spraying | threshold | 100120 / 100121 | 100111 |
| SEC-F-003 built-in 5763 silenced | overwrite | 5763 | 5760 |
| SEC-F-004 logout (SSH, console) | record | 100122 | 5502 |
| SEC-F-016 console / serial login | record; BMC part is a gap | 100123 | 5501 |

## Privileged Activity (100100-100109)

| Requirement | Kind | Rule IDs | Built on |
|---|---|---|---|
| SEC-F-005 sudo that worked (refusals excluded) | record | 100104 | sudo 5402, 5403, 5407 |
| SEC-F-005 su that worked | record | 100108 | PAM session opened 5501, `su` / `su-l` only |
| SEC-F-006 admin commands run as root | audit rule (agent) + record | 100105 | audit rule key `audit-wazuh-c`, built-in 80792 |
| SEC-F-018 failed sudo and su, also the counter for SEC-TH-007 | record | 100100 | sudo 5401, 5404, 5405, 5406; 100107; 100109 |
| SEC-F-018 su failed, with the account | helper, never the alert | 100109 | PAM auth failure 5503, `su` / `su-l` only |
| SEC-F-018 sudo refused (wrong password, not in sudoers, command not allowed) wherever it lands | helper, never the alert | 100107 | 5400, sudo success rules |
| SEC-TH-007 failed elevation, one account | threshold | 100101 / 100102 | 100100 |
| SEC-F-019 direct root login, SSH and console | alert | 100103 / 100106 | 100110 / 100123 (Host Access) |


## Install

`requirements.yml` in your project:

```yaml
---
collections:
  - name: https://github.com/bunnywkwk/wazuh_security_collection.git
    type: git
    version: main
```

```bash
ansible-galaxy collection install -r requirements.yml --force
```

## Use

```yaml
- name: Deploy security rules to the Wazuh manager
  hosts: wazuh_manager
  become: true
  roles:
    - bunnywkwk.wazuh_security.manager   # --tags sec_f_001 / host_access / record / threshold to run part of it

- name: Deploy what the agents must log
  hosts: wazuh_agents
  become: true
  roles:
    - bunnywkwk.wazuh_security.agent
```

## Variables

`roles/manager/defaults/main.yml`: `## Groups` switch, `## Rules` with one switch per requirement, then `## Settings` with what each rule needs under its ID.

```
manager_host_access                 group switch
manager_sec_f_001 ... 016           one per requirement
manager_th_001_* ... 005_*          Annex B warning / critical / timeframe
manager_service_account_patterns   local names that are service accounts whatever UID and shell (default ["^svc_"])
manager_th_003_users                privileged accounts regex
manager_account_hosts               hosts whose /etc/passwd is read (default: inventory group wazuh_agents)
manager_nologin_shells              shells that cannot log in
manager_silence_5763
manager_privileged_activity         group switch
manager_sec_f_005 ... 019           one per requirement
manager_th_007_*                    Annex B warning / critical / timeframe
manager_sec_f_019_users             accounts a direct login to is an alert (default "^root$")
```

`roles/agent/defaults/main.yml`: `agent_privileged_activity`, `agent_sec_f_006`, `agent_sec_f_006_commands` (paths audited; only the installed ones get a line).

### Service and standard account lists (SEC-TH-001, 002)

At every run the role reads `/etc/passwd` and `/etc/login.defs` on `manager_account_hosts` and sorts each account with the filter `bunnywkwk.wazuh_security.sort_accounts`:

- **standard**: UID from `UID_MIN` to `UID_MAX` with a login shell
- **service**: every other account (system UIDs, `nologin` shells, `nobody`), except root (SEC-TH-003)

The lists are the union over all hosts, written as CDB lists `/var/ossec/etc/lists/service-accounts` and `standard-accounts` (one `name:` per line) and declared in `ossec.conf`. The rules look them up with `<list field="user" lookup="match_key">`, so the rule XML never changes when accounts do. Rerun the playbook after accounts are added. Only local accounts are listed: a `svc_` name that does not exist on any agent is not counted by SEC-TH-001 (SEC-TH-004 / 005 still count it). Accounts that exist only in a directory (IdM, LDAP) are not in `/etc/passwd`, so SEC-TH-002 does not count them.

Test: `python3 tests/unit/test_accounts.py`.

Switching a rule to `false` skips it; a file deployed earlier stays until you delete it.

Built-in rule IDs, match phrases and the audit key `audit-wazuh-c` are written in the templates, not variables: they are facts of Wazuh's ruleset, not site choices (Host Access does the same). A Wazuh version that renumbers them needs a new collection version.

## Adding a requirement

1. The template in `roles/manager/templates/<group>/<kind>/`.
2. `roles/manager/tasks/<group>/sec_f_<nnn>.yml`: copy a sibling, change the ID, title, switch and template path.
3. Import it in `roles/manager/tasks/<group>/main.yml`; add `manager_sec_f_<nnn>: true` under its group in the defaults.
4. A new group: one more folder in `tasks/` and `templates/`, one import in `tasks/main.yml`, one group switch.

## Notes

- The manager role tests the ruleset with `wazuh-analysisd -t` before restarting; a broken rule stops the play and the running manager keeps its old rules.
- A failure that fires a warning is not counted again toward critical: critical fires one event late (found in Annex B testing).
- Attempts on accounts that do not exist (sshd `invalid user`, built-in 5710) are recorded (100124) but never counted: the thresholds are about real accounts, as in Annex B.
- A refused sudo line also contains `USER=root ; COMMAND=`, so it could land on a built-in success rule: 100104 excludes the refusal phrases and 100107 sends them to 100100.
- su on RHEL 9: the `(to <user>) <who> on` line gets no built-in rule and `FAILED SU` decodes no account, so su uses its PAM lines (5501 session opened, 5503 auth failure), which carry both accounts.
- SEC-F-019 rules are children of Host Access records 100110 and 100123: the task stops if SEC-F-001 or 016 is off.
- Immutable audit (`-e 2`) loads the SEC-F-006 rule only after a reboot; the agent role reports it instead of failing.
- Record rules replace the built-in alert with their own, so they carry the built-in's main groups (`sshd`, `authentication_failed` ...) to keep the default dashboards filled.
