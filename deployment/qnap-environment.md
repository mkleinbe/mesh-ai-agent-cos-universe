# QNAP Environment Evidence

Evidence available from prior operator command output:

| Item | Evidence status | Value |
|---|---|---|
| NAS model | verified previously | QTS reports `TS-X72` family |
| CPU architecture | verified previously | `x86_64` / linux amd64 |
| QTS | verified previously | 5.2.9 build 20260514 |
| Docker Engine | verified previously | 27.1.2-qnap8 |
| Docker Compose | verified previously | 2.29.1-qnap2 |
| Hostname | verified previously | `mdk-qnap6782xt` |
| LAN subnet | established deployment standard | 192.168.7.0/24 |
| Requested service IP | user-authorized | 192.168.7.60 |
| External container network | established deployment standard | `lan7` macvlan |
| NTP | verified previously | `time.google.com` configured |

Must be freshly probed before production: exact hardware model string, CPU core count, installed RAM, Container Station application version, storage pool, exact target shared-folder path, free disk space, filesystem, primary interface/Virtual Switch details, current reverse-proxy capability/configuration, certificate/FQDN inventory, outbound DNS/HTTPS, firewall/access-control state, current ports/IP conflicts, and snapshot/backup capability/state.

No unresolved item may be represented as certified production evidence.
