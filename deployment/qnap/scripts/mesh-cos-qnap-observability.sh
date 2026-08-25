#!/bin/sh
# Shared POSIX-shell observability for QNAP deployment/update tooling.
# Never log secret values, .env contents, process environments, or credential-bearing argv.

mesh_timestamp() {
  date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null || date
}

mesh_obs_init() {
  MESH_COS_COMPONENT=${1:-qnap}
  MESH_OBS_APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
  MESH_COS_LOG_ROOT=${MESH_COS_LOG_ROOT:-$MESH_OBS_APP_ROOT/logs/deployment}

  if ! mkdir -p "$MESH_COS_LOG_ROOT" 2>/dev/null; then
    MESH_COS_LOG_ROOT=${TMPDIR:-/tmp}/mesh-cos-mcp-logs
    mkdir -p "$MESH_COS_LOG_ROOT" || return 1
  fi

  new_run=0
  if [ -z "${MESH_COS_RUN_ID:-}" ]; then
    MESH_COS_RUN_ID="$(date '+%Y%m%d-%H%M%S' 2>/dev/null || date '+%s')-$$"
    new_run=1
  fi
  if [ -z "${MESH_COS_LOG_FILE:-}" ]; then
    MESH_COS_LOG_FILE="$MESH_COS_LOG_ROOT/mesh-cos-mcp-$MESH_COS_RUN_ID.log"
  fi

  : >> "$MESH_COS_LOG_FILE" || return 1
  chmod 0640 "$MESH_COS_LOG_FILE" 2>/dev/null || true
  printf '%s\n' "$MESH_COS_LOG_FILE" > "$MESH_COS_LOG_ROOT/LATEST" 2>/dev/null || true

  export MESH_COS_COMPONENT MESH_COS_LOG_ROOT MESH_COS_RUN_ID MESH_COS_LOG_FILE

  if [ "$new_run" -eq 1 ]; then
    keep=${MESH_COS_LOG_KEEP:-20}
    case "$keep" in ''|*[!0-9]*) keep=20 ;; esac
    count=0
    for old in $(ls -1t "$MESH_COS_LOG_ROOT"/mesh-cos-mcp-*.log 2>/dev/null || true); do
      count=$((count + 1))
      [ "$count" -le "$keep" ] || rm -f "$old" 2>/dev/null || true
    done
  fi

  mesh_log INFO observability_initialized "log=$MESH_COS_LOG_FILE retention=${MESH_COS_LOG_KEEP:-20}"
  mesh_log INFO run_context "uid=$(id -u 2>/dev/null || echo unknown) gid=$(id -g 2>/dev/null || echo unknown) host=$(hostname 2>/dev/null || echo unknown) pwd=$(pwd 2>/dev/null || echo unknown)"
}

mesh_log() {
  level=${1:-INFO}
  event=${2:-event}
  shift 2 2>/dev/null || true
  ts=$(mesh_timestamp)
  line="$ts level=$level run=$MESH_COS_RUN_ID component=$MESH_COS_COMPONENT event=$event"
  [ "$#" -eq 0 ] || line="$line $*"
  printf '%s\n' "$line"
  printf '%s\n' "$line" >> "$MESH_COS_LOG_FILE" 2>/dev/null || true
}

mesh_set_stage() {
  MESH_COS_STAGE=${1:-unknown}
  export MESH_COS_STAGE
  mesh_log INFO stage_enter "stage=$MESH_COS_STAGE script=${MESH_COS_SCRIPT:-unknown} line=${LINENO:-unknown}"
}

mesh_run() {
  stage=$1
  label=$2
  shift 2
  mesh_log INFO command_start "stage=$stage command=$label script=${MESH_COS_SCRIPT:-unknown} line=${LINENO:-unknown}"

  fifo="$MESH_COS_LOG_ROOT/.mesh-output-$MESH_COS_RUN_ID-$$"
  tmp="$MESH_COS_LOG_ROOT/.mesh-output-$MESH_COS_RUN_ID-$$.tmp"
  rc=0

  if command -v mkfifo >/dev/null 2>&1 && command -v tee >/dev/null 2>&1 && rm -f "$fifo" "$tmp" 2>/dev/null && mkfifo "$fifo" 2>/dev/null; then
    tee -a "$MESH_COS_LOG_FILE" < "$fifo" &
    tee_pid=$!
    "$@" > "$fifo" 2>&1 || rc=$?
    wait "$tee_pid" 2>/dev/null || true
    rm -f "$fifo" 2>/dev/null || true
  else
    "$@" > "$tmp" 2>&1 || rc=$?
    cat "$tmp" 2>/dev/null || true
    cat "$tmp" >> "$MESH_COS_LOG_FILE" 2>/dev/null || true
    rm -f "$tmp" 2>/dev/null || true
  fi

  if [ "$rc" -eq 0 ]; then
    mesh_log INFO command_end "stage=$stage command=$label rc=0"
  else
    mesh_log ERROR command_end "stage=$stage command=$label rc=$rc"
  fi
  return "$rc"
}

mesh_run_stdin_file() {
  stage=$1
  label=$2
  input_file=$3
  shift 3
  mesh_log INFO command_start "stage=$stage command=$label input=redacted-file-stream script=${MESH_COS_SCRIPT:-unknown} line=${LINENO:-unknown}"

  fifo="$MESH_COS_LOG_ROOT/.mesh-output-$MESH_COS_RUN_ID-$$"
  tmp="$MESH_COS_LOG_ROOT/.mesh-output-$MESH_COS_RUN_ID-$$.tmp"
  rc=0

  if command -v mkfifo >/dev/null 2>&1 && command -v tee >/dev/null 2>&1 && rm -f "$fifo" "$tmp" 2>/dev/null && mkfifo "$fifo" 2>/dev/null; then
    tee -a "$MESH_COS_LOG_FILE" < "$fifo" &
    tee_pid=$!
    "$@" < "$input_file" > "$fifo" 2>&1 || rc=$?
    wait "$tee_pid" 2>/dev/null || true
    rm -f "$fifo" 2>/dev/null || true
  else
    "$@" < "$input_file" > "$tmp" 2>&1 || rc=$?
    cat "$tmp" 2>/dev/null || true
    cat "$tmp" >> "$MESH_COS_LOG_FILE" 2>/dev/null || true
    rm -f "$tmp" 2>/dev/null || true
  fi

  if [ "$rc" -eq 0 ]; then
    mesh_log INFO command_end "stage=$stage command=$label rc=0"
  else
    mesh_log ERROR command_end "stage=$stage command=$label rc=$rc"
  fi
  return "$rc"
}

mesh_init_docker_config() {
  app_root=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
  DOCKER_CONFIG=${MESH_COS_DOCKER_CONFIG:-$app_root/.docker-cli}
  mkdir -p "$DOCKER_CONFIG" || return 1
  chmod 0700 "$DOCKER_CONFIG" 2>/dev/null || true
  export DOCKER_CONFIG
  mesh_log INFO docker_config "path=$DOCKER_CONFIG source=deployment-local"
}

mesh_path_evidence() {
  path=$1
  if [ -e "$path" ] || [ -L "$path" ]; then
    printf '%s\n' "PATH $path"
    ls -ldn "$path" 2>&1 || true
    if command -v stat >/dev/null 2>&1; then
      stat -c 'STAT uid=%u gid=%g mode=%a size=%s type=%F' "$path" 2>&1 || true
    fi
  else
    printf '%s\n' "PATH_MISSING $path"
  fi
}

mesh_redact_stream() {
  sed \
    -e 's/sk-[A-Za-z0-9_-][A-Za-z0-9_-]*/[REDACTED_OPENAI_KEY]/g' \
    -e 's/OPENAI_API_KEY=[^[:space:]]*/OPENAI_API_KEY=[REDACTED]/g' \
    -e 's/CONTROL_PLANE_API_KEY=[^[:space:]]*/CONTROL_PLANE_API_KEY=[REDACTED]/g' \
    -e 's/Authorization: Bearer [^[:space:]]*/Authorization: Bearer [REDACTED]/g'
}

mesh_collect_diagnostics() {
  reason=${1:-unspecified}
  [ "${MESH_DIAG_COLLECTING:-0}" = "1" ] && return 0
  MESH_DIAG_COLLECTING=1
  export MESH_DIAG_COLLECTING

  app_root=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
  state_root=${QNAP_MESH_ROOT:-$app_root/state}
  secret_file=${QNAP_TUNNEL_API_KEY_FILE:-$app_root/secrets/openai-tunnel-runtime-key}
  backup_root=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}

  {
    echo "===== MESH_DIAGNOSTIC_BEGIN ====="
    echo "timestamp=$(mesh_timestamp)"
    echo "reason=$reason"
    echo "run_id=${MESH_COS_RUN_ID:-unknown}"
    echo "component=${MESH_COS_COMPONENT:-unknown}"
    echo "stage=${MESH_COS_STAGE:-unknown}"
    echo "script=${MESH_COS_SCRIPT:-unknown}"
    echo "line=${LINENO:-unknown}"
    echo "pwd=$(pwd 2>/dev/null || echo unknown)"
    echo "docker_config=${DOCKER_CONFIG:-unset}"
    echo "-- identity --"
    id 2>&1 || true
    echo "-- platform --"
    uname -a 2>&1 || true
    [ ! -r /etc/config/uLinux.conf ] || grep -E '^(Version|Build Number)' /etc/config/uLinux.conf 2>/dev/null || true
    echo "-- docker --"
    command -v docker 2>&1 || true
    docker --version 2>&1 || true
    if command -v mesh_compose_description >/dev/null 2>&1; then
      echo "compose=$(mesh_compose_description 2>/dev/null || echo unresolved)"
    fi
    echo "-- filesystem paths --"
    mesh_path_evidence "$app_root"
    mesh_path_evidence "$state_root"
    mesh_path_evidence "$state_root/ledger"
    mesh_path_evidence "$state_root/ledger/taskledger.sqlite3"
    mesh_path_evidence "$app_root/secrets"
    mesh_path_evidence "$secret_file"
    mesh_path_evidence "$backup_root"
    echo "-- filesystem capacity --"
    df -Pk "$app_root" 2>&1 || true
    echo "-- relevant mounts --"
    mount 2>/dev/null | grep -E '/share|container-station|CE_CACHEDEV' | head -n 80 || true
    echo "-- mesh containers --"
    docker ps -a --filter 'name=mesh-cos' --format 'name={{.Names}} status={{.Status}} image={{.Image}}' 2>&1 || true
    for c in mesh-cos-mcp mesh-cos-tunnel; do
      if docker inspect "$c" >/dev/null 2>&1; then
        docker inspect -f 'container={{.Name}} running={{.State.Running}} status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}} image={{.Image}}' "$c" 2>&1 || true
      fi
    done
    if docker inspect mesh-cos-mcp >/dev/null 2>&1; then
      echo "-- mesh-cos-mcp log tail (redacted) --"
      docker logs --tail 60 mesh-cos-mcp 2>&1 | mesh_redact_stream || true
    fi
    echo "secret_contents_collected=false"
    echo "env_contents_collected=false"
    echo "tunnel_logs_collected=false"
    echo "===== MESH_DIAGNOSTIC_END ====="
  } >> "$MESH_COS_LOG_FILE" 2>&1

  mesh_log INFO diagnostic_collected "reason=$reason log=$MESH_COS_LOG_FILE"
  MESH_DIAG_COLLECTING=0
  export MESH_DIAG_COLLECTING
}

mesh_fail() {
  rc=$1
  stage=$2
  shift 2
  message=$*
  MESH_COS_STAGE=$stage
  export MESH_COS_STAGE
  mesh_log ERROR failure "stage=$stage rc=$rc script=${MESH_COS_SCRIPT:-unknown} line=${LINENO:-unknown} message=$message"
  mesh_collect_diagnostics "$message" || true
  printf 'ERROR: %s\n' "$message" >&2
  printf 'DIAGNOSTIC_LOG=%s\n' "$MESH_COS_LOG_FILE" >&2
  exit "$rc"
}
