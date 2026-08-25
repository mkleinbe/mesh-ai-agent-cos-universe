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
QCS_INSTALL=""
if command -v getcfg >/dev/null 2>&1 && [ -r /etc/config/qpkg.conf ]; then
  echo "container_station_version=$(getcfg container-station Version -f /etc/config/qpkg.conf 2>/dev/null || getcfg ContainerStation Version -f /etc/config/qpkg.conf 2>/dev/null || true)"
  QCS_INSTALL=$(getcfg container-station Install_Path -f /etc/config/qpkg.conf 2>/dev/null || getcfg ContainerStation Install_Path -f /etc/config/qpkg.conf 2>/dev/null || true)
  echo "container_station_install_path=$QCS_INSTALL"
fi
if command -v docker >/dev/null 2>&1; then
  docker version 2>/dev/null || true
  docker compose version 2>/dev/null || true
  echo "docker_compose_plugin_path=$(docker info --format '{{range .ClientInfo.Plugins}}{{if eq .Name "compose"}}{{.Path}}{{end}}{{end}}' 2>/dev/null || true)"
  for p in \
    /usr/local/lib/docker/cli-plugins/docker-compose \
    /usr/libexec/docker/cli-plugins/docker-compose \
    "$QCS_INSTALL/usr/local/lib/docker/cli-plugins/docker-compose" \
    "$QCS_INSTALL/usr/libexec/docker/cli-plugins/docker-compose" \
    "$QCS_INSTALL/bin/docker-compose" \
    "$QCS_INSTALL/bin/system-docker-compose" \
    "$QCS_INSTALL/usr/bin/.libs/docker-compose"; do
    [ -n "$p" ] || continue
    if [ -x "$p" ]; then
      echo "compose_candidate=$p"
      "$p" version 2>/dev/null || true
    fi
  done
  docker network inspect lan7 2>/dev/null || true
  docker network ls 2>/dev/null || true
  docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null || true
fi
ip addr 2>/dev/null || ifconfig 2>/dev/null || true
ip route 2>/dev/null || route -n 2>/dev/null || true
mount 2>/dev/null || true
df -k 2>/dev/null || true
for p in "/share/Docker" "/share/Docker/cos-mcp" "/share/QNAP NAS/Mike Home/MCP/CoS/Backups"; do
  echo "path=$p"
  readlink -f "$p" 2>/dev/null || true
  df -k "$p" 2>/dev/null || true
  ls -ldn "$p" 2>/dev/null || true
done
[ -r /etc/config/ntp.conf ] && cat /etc/config/ntp.conf 2>/dev/null || true

echo "# Probe is read-only. Review output before updating deployment/qnap-environment.md."
