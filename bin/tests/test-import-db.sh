#!/usr/bin/env bash
set -Eeuo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
temporary_directory="$(mktemp -d)"
trap 'rm -rf "$temporary_directory"' EXIT
export IMPORT_TEST_LOG="$temporary_directory/commands"
dump_file="$temporary_directory/test.sql"
printf 'SELECT 1;\n' > "$dump_file"

docker() {
  if [[ "$*" == "compose version" ]]; then
    return 0
  fi
  printf '%s\n' "$*" >> "$IMPORT_TEST_LOG"
  case "$*" in
    "compose --profile prodlike ps --status running --services")
      printf '%s\n' "$RUNNING_SERVICES"
      ;;
    "compose --profile prodlike stop backend backend-prod")
      return "$FAIL_STOP"
      ;;
    *"DROP DATABASE"*)
      printf 'database-replaced\n' >> "$IMPORT_TEST_LOG"
      ;;
    *'mysql --user=root "$MYSQL_DATABASE"')
      cat > /dev/null
      ;;
  esac
}
export -f docker

check_import() {
  local services="$1"
  local expected_backends="$2"
  : > "$IMPORT_TEST_LOG"
  RUNNING_SERVICES="$services" FAIL_STOP=0 \
    bash "$repository_root/bin/import-db.sh" "$dump_file" --yes > "$temporary_directory/output" 2>&1
  grep -Fxq 'compose --profile prodlike stop backend backend-prod' "$IMPORT_TEST_LOG"
  grep -Fxq 'database-replaced' "$IMPORT_TEST_LOG"
  grep -Fxq "compose --profile prodlike up -d $expected_backends" "$IMPORT_TEST_LOG"
  printf 'PASS: restores %s\n' "$expected_backends"
}

check_import $'db\nbackend\nfrontend' backend
check_import $'db\nbackend-prod\nnginx' backend-prod
check_import $'db\nbackend\nbackend-prod' 'backend backend-prod'
check_import db backend

: > "$IMPORT_TEST_LOG"
if RUNNING_SERVICES=backend-prod FAIL_STOP=1 \
  bash "$repository_root/bin/import-db.sh" "$dump_file" --yes > "$temporary_directory/output" 2>&1; then
  echo 'FAIL: import continued after stopping failed' >&2
  exit 1
fi
if grep -Fq 'database-replaced' "$IMPORT_TEST_LOG"; then
  echo 'FAIL: database was replaced after stopping failed' >&2
  exit 1
fi
printf 'PASS: stop failure prevents database replacement\n'