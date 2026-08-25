# QNAP Environment Evidence

## Certified probe snapshot

Probe captured **2026-08-25 07:31:39 EDT** from `mdk-qnap6782xt`.

| Item | Status | Verified value |
|---|---|---|
| NAS model | verified | QTS reports `TS-X72` family |
| CPU architecture | verified | `x86_64` / `linux/amd64` |
| CPU cores | verified | 4 |
| Installed RAM | verified | 65,757,252 KiB, approximately 62.7 GiB |
| Kernel | verified | Linux 5.10.60-qnap |
| QTS | verified | 5.2.10 build 20260731 |
| Docker Engine | verified | 27.1.2-qnap8, API 1.46, linux/amd64 |
| containerd | verified | 1.7.20 |
| runc | verified | 1.1.13 |
| Docker Compose | verified | 2.29.1-qnap2 |
| Hostname | verified | `mdk-qnap6782xt` |
| NAS LAN address | verified | `192.168.7.20/24` on `qvs0` |
| Default gateway | verified | `192.168.7.1` |
| Primary physical interface | verified | `eth1`, enslaved to `qvs0` |
| External container network | verified | `lan7`, QNAP `qnet`, interface `eth1` |
| `lan7` subnet/gateway | verified | `192.168.7.0/24`, gateway `192.168.7.1` |
| Requested service IP | operator-authorized | `192.168.7.60` |
| Existing `lan7` container IPs | verified at probe time | `192.168.7.71` honcho-api; `192.168.7.72` graphiti-mcp |
| Private Docker bridges | verified | `172.29.0.0/22`, `172.29.4.0/22`, `172.29.8.0/22`, plus Docker/LXC/LXD 10.0.x networks |
| mesh-cos private subnet | verified non-overlap at probe time | `172.30.60.0/29` |
| Primary Docker storage filesystem | verified | ext4 on `/share/CE_CACHEDEV2_DATA` |
| Primary Docker storage free space | verified | 2,057,517,080 KiB, approximately 1.92 TiB free |
| Primary Docker storage utilization | verified | 96% used |
| Secondary cache storage | verified | ext4 `/share/CACHEDEV3_DATA`, 99% used, approximately 31.4 GiB free |
| Snapshot subsystem | evidenced | multiple read-only CE snapshot mounts present |
| Application deployment root | operator-authorized | `/share/Docker/cos-mcp/` |
| Script execution root | operator-authorized | `/share/Docker` |
| Backup destination | operator-authorized | `/share/QNAP NAS/Mike Home/MCP/CoS/Backups` |

## Important QNAP path behavior

`/share` itself is a small tmpfs namespace and is not the capacity-bearing filesystem. Shared-folder paths below `/share/...` resolve to the QNAP data volumes. Deployment and preflight must evaluate the resolved target path, not `df /share`.

The application uses the stable operator path `/share/Docker/cos-mcp/`, with canonical runtime state under `/share/Docker/cos-mcp/state/`. The backup path contains spaces and must always be shell-quoted exactly as `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` or passed as one quoted argument.

## Resource decision

The main MCP container is capped at **2 CPUs and 24 GiB RAM** with **no PID limit**. On the probed 4-core, 62.7-GiB NAS this leaves approximately half of CPU capacity and more than 38 GiB RAM outside the MCP limit for QTS, storage services, Container Station, and other containers. The tunnel sidecar remains separately constrained to 0.25 CPU and 256 MiB RAM and also has no PID limit.

## Storage risk

The primary Docker volume is 96% allocated but still has about 1.92 TiB free. This is not an immediate absolute-capacity blocker for mesh-cos-mcp, but it is an operational warning because QNAP snapshot/storage behavior can become constrained at high percentage utilization. Production preflight requires at least 20 GiB free and the operator should monitor pool utilization independently.

## Remaining live checks

The probe did not conclusively capture the Container Station application-package version, current QNAP firewall/access-control policy, reverse-proxy/certificate inventory, external DNS/HTTPS reachability, exact NTP source, exact shared-folder UID/GID/ACL state, or whether another non-Docker LAN device is already using `192.168.7.60`. The deployment scripts validate what can be checked locally and leave these items visible for operator confirmation.
