#!/bin/sh
# QNAP Container Station Compose V2 discovery helper. Source this file.

mesh_qcs_install_path() {
  qcs=""
  if [ -x /sbin/getcfg ] && [ -r /etc/config/qpkg.conf ]; then
    qcs=$(/sbin/getcfg container-station Install_Path -f /etc/config/qpkg.conf 2>/dev/null || true)
    [ -n "$qcs" ] || qcs=$(/sbin/getcfg ContainerStation Install_Path -f /etc/config/qpkg.conf 2>/dev/null || true)
  fi
  printf '%s' "$qcs"
}

mesh_compose_v2() {
  "$@" version 2>/dev/null | grep -Eq '(^|[[:space:]])v?2\.'
}

mesh_resolve_compose() {
  command -v docker >/dev/null 2>&1 || return 1

  if mesh_compose_v2 docker compose; then
    MESH_COMPOSE_MODE=docker-subcommand
    MESH_COMPOSE_BIN=""
    export MESH_COMPOSE_MODE MESH_COMPOSE_BIN
    return 0
  fi

  plugin=$(docker info --format '{{range .ClientInfo.Plugins}}{{if eq .Name "compose"}}{{.Path}}{{end}}{{end}}' 2>/dev/null || true)
  qcs=$(mesh_qcs_install_path)

  for candidate in \
    "$plugin" \
    /usr/local/lib/docker/cli-plugins/docker-compose \
    /usr/libexec/docker/cli-plugins/docker-compose \
    "$qcs/usr/local/lib/docker/cli-plugins/docker-compose" \
    "$qcs/usr/libexec/docker/cli-plugins/docker-compose" \
    "$qcs/bin/docker-compose" \
    "$qcs/bin/system-docker-compose" \
    "$qcs/usr/bin/.libs/docker-compose"; do
    [ -n "$candidate" ] || continue
    if [ -x "$candidate" ] && mesh_compose_v2 "$candidate"; then
      MESH_COMPOSE_MODE=direct-plugin
      MESH_COMPOSE_BIN=$candidate
      export MESH_COMPOSE_MODE MESH_COMPOSE_BIN
      return 0
    fi
  done
  return 1
}

mesh_compose() {
  [ -n "${MESH_COMPOSE_MODE:-}" ] || mesh_resolve_compose || return 127
  case "$MESH_COMPOSE_MODE" in
    docker-subcommand) docker compose "$@" ;;
    direct-plugin) "$MESH_COMPOSE_BIN" "$@" ;;
    *) return 127 ;;
  esac
}

mesh_compose_description() {
  case "${MESH_COMPOSE_MODE:-}" in
    docker-subcommand) printf '%s' 'docker compose' ;;
    direct-plugin) printf '%s' "$MESH_COMPOSE_BIN" ;;
    *) printf '%s' unresolved ;;
  esac
}
