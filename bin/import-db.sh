#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  echo "Usage: $0 path/to/dump.sql[.gz] [--yes]" >&2
}

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    echo "Docker Compose is required." >&2
    exit 1
  fi
}

assume_yes=false
dump_file=""

for argument in "$@"; do
  case "$argument" in
    --yes)
      assume_yes=true
      ;;
    *.sql|*.sql.gz)
      if [[ -n "$dump_file" ]]; then
        usage
        exit 1
      fi
      dump_file="$argument"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$dump_file" || ! -f "$dump_file" ]]; then
  echo "SQL dump not found: ${dump_file:-<missing>}" >&2
  usage
  exit 1
fi

if [[ "$assume_yes" != true ]]; then
  if [[ ! -t 0 ]]; then
    echo "Refusing to replace the local database without an interactive terminal or --yes." >&2
    exit 1
  fi

  echo "This will replace the Docker Compose local database with:"
  echo "  $dump_file"
  read -r -p "Continue? [y/N] " confirmation
  if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Import cancelled."
    exit 0
  fi
fi

echo "Starting the local database..."
compose up -d db

echo "Waiting for MySQL..."
for attempt in {1..60}; do
  if compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqladmin ping --host=localhost --user=root --silent' >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" -eq 60 ]]; then
    echo "MySQL did not become ready." >&2
    exit 1
  fi
  sleep 1
done

running_services="$(compose --profile prodlike ps --status running --services)"
backends=()
while IFS= read -r service; do
  case "$service" in
    backend|backend-prod)
      backends+=("$service")
      ;;
  esac
done <<< "$running_services"
if [[ "${#backends[@]}" -eq 0 ]]; then
  backends=(backend)
fi

echo "Stopping application backends during import..."
compose --profile prodlike stop backend backend-prod

echo "Recreating the local application database..."
compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --user=root --execute="DROP DATABASE IF EXISTS \`$MYSQL_DATABASE\`; CREATE DATABASE \`$MYSQL_DATABASE\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'

echo "Importing $dump_file..."
if [[ "$dump_file" == *.gz ]]; then
  gzip -dc "$dump_file" | compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --user=root "$MYSQL_DATABASE"'
else
  compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --user=root "$MYSQL_DATABASE"' < "$dump_file"
fi

echo "Starting application backends and applying migrations..."
compose --profile prodlike up -d "${backends[@]}"
echo "Database import complete. Follow startup with: docker compose --profile prodlike logs -f ${backends[*]}"
