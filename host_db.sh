#!/bin/bash

set -euo pipefail  # safer bash

#is used to make shell scripts safer and more predictable. Here's what each flag does:

#Option	Meaning
#-e	Exit immediately if any command returns a non-zero status.
#-u	Treat unset variables as an error and exit immediately.
#-o pipefail	The pipeline returns the exit status of the last command to fail.

# chmod +x host_db.sh

# === Default Configuration ===
DEFAULT_PORT=8000
DEFAULT_TITLE="Maritime DB"
LOGFILE="/tmp/datasette_host.log"

# === Usage Help ===
usage() {
  echo "Usage: $0 --db /full/path/to.db [--port 8000] [--title 'Viewer Title']"
  exit 1
}
# ./host_db.sh --db /Users/kaaso/Documents/Tordenskjold/Data/Satellite_Data/db_test/downloads.db --port 8080 --title "My Secure DB"
# ./host_db.sh --db /Users/kaaso/Documents/Tordenskjold/Data/Satellite_Data/db_test/downloads.db --port 8080 --title "My Secure DB" 


# === Parse Arguments ===
DB_PATH=""
PORT="$DEFAULT_PORT"
TITLE="$DEFAULT_TITLE"

while [[ $# -gt 0 ]]; do
  case $1 in
    --db)
      DB_PATH="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# === Validate Inputs ===
if [[ ! -f "$DB_PATH" ]]; then
  echo "Error: DB file does not exist: $DB_PATH"
  usage
fi

# === Secure Dependencies Check ===
REQUIRED_TOOLS=("datasette" "python3")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo "Error: $tool not found. Please install it."
        exit 1
    fi
done

# === Optional: Obfuscate IP/Hostname ===
export PS1="> "
unset HOSTNAME
unset SSH_CLIENT
unset SSH_CONNECTION


METAFILE="/tmp/datasette_metadata.json"
cat > "$METAFILE" <<EOF
{
  "title": "$TITLE",
  "license": "Internal Only"
}
EOF

# === Main Loop to Maintain Secure Hosting ===
while true; do
  echo "[$(date)] Starting datasette for: $DB_PATH" >> "$LOGFILE"
  
  # Kill previous instance if needed (safe local-only port)
  fuser -k "${PORT}/tcp" &> /dev/null || true

  # Run datasette (read-only, safe options)
  datasette serve "$DB_PATH" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --metadata "$METAFILE" \
  --setting allow_download false \
  --cors \
  >> "$LOGFILE" 2>&1

  echo "[$(date)] Datasette exited. Restarting in 5 sec..." >> "$LOGFILE"
  sleep 5
done
