# database
can be used for defense deliverbale to keep track of the satellite images..

nohup ./host_db.sh --db /mnt/hdd/Data/SAR/Sentinel1/IW/DbTest/downloads.db --port 8080 --title "DTU Security Satellite image database for FE" > data/logs/host_db_$(date +"%Y%m%d_%H%M%S").log.out 2>&1 &


lsof -i :8080
chekc the log
tail -f /tmp/datasette_host.log



assert that it is read only
sqlite3 /tmp/readonly_downloads.db "PRAGMA query_only;"

