#!/bin/bash

# Define users, ports, and plaintext passwords
USER_LIST=("student" "group1" "group2" "group3" "group4")

declare -A USERS_PORTS=(
    [student]=8880
    [group1]=8881
    [group2]=8882
    [group3]=8883
    [group4]=8884
)

declare -A USERS_PASSWORDS=(
    [student]="student"
    [group1]="group1"
    [group2]="group2"
    [group3]="group3"
    [group4]="group4"
)

if [[ "$EUID" -ne 0 ]]; then
	echo "This script must be run as root."
	exit 1
fi

# Prompt for confirmation
read -p "Are you sure you would like to delete and recreate all student accounts? (yes/no): " CONFIRMATION
if [[ "$CONFIRMATION" != "yes" ]]; then
    echo "Aborting operation."
    exit 1
fi

echo "Deleting existing users matching student' or 'group'..."
for user in $(awk -F: '{ print $1 }' /etc/passwd | grep -E '^group[0-9]*$|^student$'); do
    echo "Deleting user: $user"
    service="jupyter-${user}.service"
    systemctl stop "$service"
    pkill -u "$user"
    userdel -r "$user"
done

echo "Creating users, setting passwords, and configuring services..."
for user in "${USER_LIST[@]}"; do
    port="${USERS_PORTS[$user]}"
    password="${USERS_PASSWORDS[$user]}"
    echo "Creating user: $user"
    adduser --gecos "" --disabled-password "$user"
    echo "$user:$password" | chpasswd

    echo "Generating password hash for $user"
    HASH=$(python3 -c "from notebook.auth import passwd; print(passwd('${password}'))")

    # Create Jupyter script
    jupyter_dir="/home/$user/Desktop/Arm"
    mkdir -p "$jupyter_dir"
    chown "$user:$user" "$jupyter_dir"

    jupyter_script="$jupyter_dir/jupyter.sh"
    cat > "$jupyter_script" <<EOF
#!/bin/bash
source /home/jetson/dofbot_ws/devel/setup.bash
jupyter lab \\
  --port=${port} \\
  --no-browser \\
  --ip=0.0.0.0 \\
  --LabApp.password='${HASH}'
EOF

    chmod +x "$jupyter_script"
    chown "$user:$user" "$jupyter_script"

    # Create systemd service
    service_file="/etc/systemd/system/jupyter-${user}.service"
    cat > "$service_file" <<EOF
[Unit]
Description=Jupyter Notebook Service for $user

[Service]
Type=simple
User=$user
ExecStart=/bin/sh -c "bash $jupyter_script"
WorkingDirectory=/home/$user/Desktop
Restart=always
StartLimitInterval=1min

[Install]
WantedBy=multi-user.target
EOF
done

echo "Reloading systemd and starting services..."
systemctl daemon-reexec
systemctl daemon-reload

for user in "${!USERS_PORTS[@]}"; do
    service="jupyter-${user}.service"
    systemctl enable "$service"
    systemctl start "$service"
    echo "Started service: $service"
done

echo "All student accounts and Jupyter services set up successfully."

