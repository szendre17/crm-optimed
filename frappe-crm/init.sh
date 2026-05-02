#!/bin/bash

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists, skipping init"
    cd frappe-bench
    bench start
else
    echo "Creating new bench..."
fi

bench init --skip-redis-config-generation frappe-bench --version version-15

cd frappe-bench

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove redis, watch from Procfile
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

bench get-app crm --branch main

bench new-site crm.localhost \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

bench --site crm.localhost install-app crm

# Install optimed_crm from workspace (symlink keeps code editable on host)
if [ -d "/workspace/optimed_crm" ]; then
    ln -sf /workspace/optimed_crm /home/frappe/frappe-bench/apps/optimed_crm
    uv pip install --quiet -e /home/frappe/frappe-bench/apps/optimed_crm \
        --python /home/frappe/frappe-bench/env/bin/python
    # Register app in apps.txt (bench install-app requires this)
    APPS_TXT=/home/frappe/frappe-bench/sites/apps.txt
    if ! grep -qx "optimed_crm" "$APPS_TXT"; then
        # Ensure file ends with newline before appending
        [ -n "$(tail -c 1 "$APPS_TXT")" ] && echo "" >> "$APPS_TXT"
        echo "optimed_crm" >> "$APPS_TXT"
    fi
    bench --site crm.localhost install-app optimed_crm
fi

bench --site crm.localhost set-config developer_mode 1
bench --site crm.localhost set-config mute_emails 1
bench --site crm.localhost set-config server_script_enabled 1
bench --site crm.localhost clear-cache
bench use crm.localhost

bench start
