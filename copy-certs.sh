#!/bin/sh
# Copy this script to /bin (`sudo cp ./copy-certs.sh /bin`), make it executable (`sudo chmod +x /bin/copy-certs.sh`) and add the output of the following command to the root crontab (use `sudo crontab -e`):
# ```
# echo "0 0 * * * /bin/copy-certs.sh $(pwd) $USER"
# ```

set -e

if [ "$(id -u)" -ne 0 ]; then 
    echo "$(date) Please run this script as root."
    exit 1
fi

if [ "$#" -ne 2 ]; then
    echo "$(date) Must supply a project directory and a user who is running the game server."
    echo "$(date) If you are unsure which arguments to choose, cd into your project directory and run \"\$(pwd) \$USER\""
    exit 1
fi

project_dir="$1"
server_usr="$2"

if [ ! -d "$project_dir" ]; then
    echo "$(date) Project directory $project_dir does not exist. Check you spelled it correctly and you've cloned your project into the correct location."
    exit 1
fi

server_dir="$project_dir/server"
if [ ! -d "$project_dir" ]; then
    echo "$(date) Project directory exists, but could not find server folder ($server_dir). Check you cloned the repository correctly and haven't accidentally moved or deleted something."
    exit 1
fi

# Run the Let's Encrypt renewals if they're up for renewal
echo "$(date) Attempting to renew Let's Encrypt certificates..."
certbot renew

# Copy the renewed certificates into the game server directory
certs_dir="$server_dir/certs"
if [ ! -d "$certs_dir" ]; then
    echo "$(date) Certificates folder not found. Automatically creating $certs_dir..."
    mkdir "$certs_dir"
    chown "$server_usr" "$certs_dir"
fi

echo "$(date) Attempting to copy Let's Encrypt certificates to $certs_dir"
cp /etc/letsencrypt/live/godmmo.tx2600.net/fullchain.pem "$certs_dir/server.crt"
cp /etc/letsencrypt/live/godmmo.tx2600.net/privkey.pem "$certs_dir/server.key"
echo "$(date) Done"

echo "$(date) Attempting to change ownership of $certs_dir/server.crt and $certs_dir/server.key to $server_usr"
chown "$server_usr" "$certs_dir/server.crt"
chown "$server_usr" "$certs_dir/server.key"
echo "$(date) Done"

exit 0