#!/bin/sh
set -u

echo "# mesh-cos-mcp QNAP environment probe"
echo "timestamp=$(date 2>/dev/null || true)"
echo "hostname=$(hostname 2>/dev/null || true)"
echo "uname=$(uname -a 2>/dev/null || true)"
echo "arch=$(uname -m 2>/dev/null || true)"
echo "cpu_count=$(grep -c '^processor' /proc/cpuinfo 2>/dev/null || true)"
echo "memory_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || true)"
if [ -r /etc/config/uLinux.conf ]; then
  echo "qts_version=$(grep '^Version' /etc/config/uLinux.conf 2>/dev/null | head -n 1)"
  echo "qts_build=$(grep '^Build Number' /etc/config/uLinux.conf 2>/dev/null | head -n 1)"
  echo "model=$(grep '^Model' /etc/config/uLinux.conf 2>/dev/null | head -n 1)"
fi
command -v docker >/dev/null 2>&1 && docker version 2>/dev/null || true
command -v docker >/dev/null 2>&1 && docker compose version 2>/dev/null || true
command -v docker >/dev/null 2>&1 && docker network inspect lan7 2>/dev/null || true
command -v docker >/dev/null 2>&1 && docker network ls 2>/dev/null || true
command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null || true
ip addr 2>/dev/null || ifconfig 2>/dev/null || true
ip route 2>/dev/null || route -n 2>/dev/null || true
mount 2>/dev/null || true
df -k 2>/dev/null || true
[ -r /etc/config/ntp.conf ] && cat /etc/config/ntp.conf 2>/dev/null || true

echo "# Probe is read-only. Review output before adding it to deployment/qnap-environment.md."
