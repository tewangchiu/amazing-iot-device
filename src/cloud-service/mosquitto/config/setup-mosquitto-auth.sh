#!/bin/bash
# Script to create/update Mosquitto authentication credentials

# Check if we're running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Define variables
PASSWD_FILE="/mosquitto/config/mosquitto_passwd"
DEFAULT_USER="iotdevice"
DEFAULT_PASS="iotpassword"

# Function to create a new password file
create_new_password_file() {
  echo "Creating a new password file with default user..."
  touch $PASSWD_FILE
  mosquitto_passwd -b $PASSWD_FILE $DEFAULT_USER $DEFAULT_PASS
  echo "Created user '$DEFAULT_USER' with password '$DEFAULT_PASS'"
}

# Function to add a new user
add_user() {
  read -p "Enter username: " username
  read -s -p "Enter password: " password
  echo
  mosquitto_passwd -b $PASSWD_FILE $username $password
  echo "User '$username' added/updated"
}

# Function to delete a user
delete_user() {
  read -p "Enter username to delete: " username
  mosquitto_passwd -D $PASSWD_FILE $username
  echo "User '$username' deleted"
}

# Main menu
echo "Mosquitto Authentication Setup"
echo "============================="

# Check if the password file exists
if [ ! -f "$PASSWD_FILE" ]; then
  echo "Password file doesn't exist."
  read -p "Create new password file with default user? (y/n): " choice
  if [ "$choice" = "y" ]; then
    create_new_password_file
  else
    echo "Exiting without creating password file."
    exit 0
  fi
else
  echo "Password file exists at $PASSWD_FILE"
fi

# Show menu
while true; do
  echo
  echo "Choose an option:"
  echo "1. Add/Update a user"
  echo "2. Delete a user"
  echo "3. Exit"
  read -p "Selection: " option

  case $option in
    1) add_user ;;
    2) delete_user ;;
    3) 
      echo "Exiting."
      exit 0
      ;;
    *) echo "Invalid option. Please try again." ;;
  esac
done