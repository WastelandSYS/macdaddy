#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/usr/local/bin"
INSTALL_NAME="macdaddy"
BACKUP_DIR="/var/lib/macdaddy"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="${SCRIPT_DIR}/macdaddy.py"
TARGET_SCRIPT="${INSTALL_DIR}/${INSTALL_NAME}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "Please run as root: sudo ./install.sh" >&2
    exit 1
fi

if [[ ! -f "${SOURCE_SCRIPT}" ]]; then
    echo "Could not find macdaddy.py next to install.sh" >&2
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer currently supports apt-based systems only." >&2
    echo "Install python3, macchanger, and iproute2 manually, then copy macdaddy.py to ${TARGET_SCRIPT}." >&2
    exit 1
fi

echo "Installing dependencies: python3, macchanger, iproute2..."
apt-get update
apt-get install -y python3 macchanger iproute2

echo "Installing ${INSTALL_NAME} to ${TARGET_SCRIPT}..."
install -d -m 0755 "${INSTALL_DIR}"
install -m 0755 "${SOURCE_SCRIPT}" "${TARGET_SCRIPT}"

echo "Preparing system-wide backup directory at ${BACKUP_DIR}..."
install -d -m 0755 "${BACKUP_DIR}"

cat <<EOF
Installation complete.

Run MacDaddy from anywhere with:
  sudo ${INSTALL_NAME}

Useful commands:
  ${INSTALL_NAME} --help
  sudo ${INSTALL_NAME} backup
  sudo ${INSTALL_NAME} list

Default root/system backup file:
  ${BACKUP_DIR}/mac_backup.txt
EOF
