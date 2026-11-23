# Changelog

## 0.7.1 (2026-11-23)
- SEC-TH-001 / 002 list lookup uses field="user" (Wazuh's name for the account field); field="dstuser" never matched, found by verify.yml.

## 0.7.0 (2026-11-23)
- SEC-F-002 also records failed logins for accounts that do not exist (100124, on built-in 5710), searchable as sec_f_002; not counted by SEC-TH-001 to 005.
- Levels aligned with the validated Annex B write-up: SEC-TH-001 8 / 12, SEC-TH-004 critical 13.

## 0.6.0 (2026-11-23)
- SEC-TH-001 / 002 look the account up in CDB lists etc/lists/service-accounts and standard-accounts (templates/host_access/list/), declared in ossec.conf, instead of a regex in the rule.
- manager_th_001_extra_users replaced by manager_service_account_patterns (default ["^svc_"]): local accounts matching it go to the service list.
- Defaults: rule switches on top, settings per rule below.

## 0.5.0 (2026-11-23)
- SEC-TH-001 and 002 accounts read from /etc/passwd on the agents at every run, with UID_MIN / UID_MAX from /etc/login.defs: standard = UID_MIN to UID_MAX with a login shell, service = every other account except root.
- New filter plugin bunnywkwk.wazuh_security.sort_accounts, test in tests/unit/test_accounts.py.
- manager_th_001_users replaced by manager_th_001_extra_users (default "^svc_"); new manager_account_hosts, manager_nologin_shells.

## 0.4.0 (2026-11-23)
- Privileged Activity parked: manager tasks and templates and the whole agent role removed, to focus on Host Access. Restore notes are kept outside the repo.
- Templates split by kind: templates/host_access/record/, threshold/, overwrite/.
- 100110 no longer skips root (that only made sense next to SEC-F-019).

## 0.3.0 (2026-11-23)
- One task file and one rules file per requirement, like the CIS roles: tasks/<group>/sec_f_<nnn>.yml, /var/ossec/etc/rules/<id>.xml.
- Group switches manager_host_access, manager_privileged_activity, agent_privileged_activity replace manager_groups / agent_groups.
- manager_elevation_failure_sids renamed manager_sec_f_018_sids.
- Root SSH logins go to SEC-F-019 (100103, also tagged sec_f_001); 100110 skips root while SEC-F-019 is on.
- Tags per requirement (sec_f_001), group (host_access) and kind (record, threshold, alert, audit_rule).

## 0.2.0 (2026-11-23)
- New group: host_access (SEC-F-001, 002, 004, 016 record rules; SEC-F-003 thresholds SEC-TH-001 to 005; built-in 5763 silenced).
- privileged_activity: SEC-F-005 record rule (100104); rule IDs moved to 100100-100109; SEC-TH-007 levels 9 / 13.
- Role defaults: one defaults/main.yml per role.

## 0.1.0 (2026-11-23)
- First group: privileged_activity (SEC-F-006, SEC-F-018 + SEC-TH-007, SEC-F-019).
