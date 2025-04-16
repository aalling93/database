#!/bin/bash
set -euo pipefail  # safer bash

# del
#  ./host_db.sh --db /Users/kaaso/Documents/Tordenskjold/Data/Satellite_Data/db_test/downloads.db --port 8080 --title "My Secure DB"
# ./host_db.sh --db /mnt/hdd/Data/SAR/Sentinel1/IW/DbTest/downloads.db --port 8080 --title "My Secure DB" 
# nohup ./host_db.sh --db /mnt/hdd/Data/SAR/Sentinel1/IW/DbTest/downloads.db --port 8080 --title "DTU Security Satellite image database for FE" > data/logs/host_db_$(date +"%Y%m%d_%H%M%S").log.out 2>&1 &
#
#
#
#
#
#is used to make shell scripts safer and more predictable. Here's what each flag does:
#
#Option	Meaning
#-e	Exit immediately if any command returns a non-zero status.
#-u	Treat unset variables as an error and exit immediately.
#-o pipefail	The pipeline returns the exit status of the last command to fail.
#
# remember to make the script executable, yo. 
# chmod +x host_db.sh
#
#
#
#
#
#
#
#
#
#
#
# === Default Configuration ===
DEFAULT_PORT=8000
DEFAULT_TITLE="DTU Security Satellite DB"
LOGFILE="/tmp/datasette_host.log"



# === Usage Help ===
usage() {
  echo "Usage: $0 --db /full/path/to.db [--port 8000] [--title 'Viewer Title'] [--log-file /path/to/log]"
  exit 1
}


# === Parse Arguments ===
DB_PATH=""
PORT="$DEFAULT_PORT"
TITLE="$DEFAULT_TITLE"

while [[ $# -gt 0 ]]; do
  case $1 in
    --db)
      DB_PATH="$2"; shift 2 ;;
    --port)
      PORT="$2"; shift 2 ;;
    --title)
      TITLE="$2"; shift 2 ;;
    --log-file)
      LOGFILE="$2"; shift 2 ;;
    *)
      echo "Unknown option: $1"; usage ;;
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


# TODO: change the json so it is easier to display the image.. Or whatever.
# we show the encoded string as an image, hide the original, and make it possible to download if you want...  (when download table, the string is downlaod not the iamge)
METAFILE="/tmp/datasette_metadata.json"
cat > "$METAFILE" <<EOF
{
  "title": "$TITLE",
  "license": "Internal Only",
}
EOF



# === Kinda Secure Hosting. Probabily good for F.. ===
mkdir -p "$(dirname "$LOGFILE")"
echo "[INFO] Logging to: $LOGFILE"

while true; do
  echo "[$(date)] ==========================================================" >> "$LOGFILE"
  echo "[$(date)] Launching datasette for DB: $DB_PATH" >> "$LOGFILE"
  echo "[$(date)] Using port: $PORT | Title: '$TITLE'" >> "$LOGFILE"
  echo "[$(date)] Metadata file: $METAFILE" >> "$LOGFILE"
  
  echo "[$(date)] Full command: datasette serve \"$DB_PATH\" --host 0.0.0.0 --port $PORT --metadata $METAFILE --setting allow_download false --cors" >> "$LOGFILE"


  # Kill previous instance if needed (safe local-only port)
  echo "[$(date)] Checking and killing previous datasette instance on port $PORT if running..." >> "$LOGFILE"
  fuser -k "${PORT}/tcp" &>> "$LOGFILE" || echo "[$(date)] No process on port $PORT" >> "$LOGFILE"




  # Run datasette (read-only, safe options)
  echo "[$(date)] Starting datasette..." >> "$LOGFILE"
  datasette serve "$DB_PATH" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --metadata "$METAFILE" \
  --setting allow_download false \
  --setting sql_time_limit_ms 10000 \
  --cors \
  >> "$LOGFILE" 2>&1

  EXIT_CODE=$?

  echo "[$(date)] ⚠️ Datasette exited with code $EXIT_CODE. Restarting in 5 sec..." >> "$LOGFILE"
  sleep 5
done
