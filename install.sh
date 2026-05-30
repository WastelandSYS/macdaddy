#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="macdaddy"
INSTALL_ROOT="/opt/${APP_NAME}"
INSTALL_SCRIPT="${INSTALL_ROOT}/macdaddy.py"
COMMAND_PATH="/usr/local/bin/${APP_NAME}"
BACKUP_DIR="/var/lib/${APP_NAME}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="${SCRIPT_DIR}/macdaddy.py"
DEPENDENCIES=(python3 macchanger iproute2)

info() { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
success() { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

on_error() {
    fail "Installation failed on line ${1}. No user backup files were removed."
}
trap 'on_error ${LINENO}' ERR

require_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        fail "Please run as root: sudo ./install.sh"
    fi
}

require_source() {
    if [[ ! -f "${SOURCE_SCRIPT}" ]]; then
        fail "Could not find macdaddy.py next to install.sh."
    fi
}

install_dependencies() {
    if command -v apt-get >/dev/null 2>&1; then
        info "Installing dependencies: ${DEPENDENCIES[*]}"
        export DEBIAN_FRONTEND=noninteractive
        apt-get update
        apt-get install -y "${DEPENDENCIES[@]}"
    else
        warn "apt-get was not found. Skipping automatic dependency installation."
        warn "Install these packages manually for your distribution: ${DEPENDENCIES[*]}"
    fi
}

verify_dependencies() {
    local missing=()
    for command in python3 macchanger ip; do
        if ! command -v "${command}" >/dev/null 2>&1; then
            missing+=("${command}")
        fi
    done

    if (( ${#missing[@]} > 0 )); then
        fail "Missing required command(s): ${missing[*]}"
    fi
}

prepare_command_path() {
    if [[ -e "${COMMAND_PATH}" && ! -L "${COMMAND_PATH}" ]]; then
        if grep -q "MacDaddy" "${COMMAND_PATH}" 2>/dev/null; then
            info "Replacing legacy MacDaddy command at ${COMMAND_PATH}"
            rm -f "${COMMAND_PATH}"
        else
            fail "${COMMAND_PATH} already exists and does not look like MacDaddy. Remove it manually or choose another command path."
        fi
    fi
}

install_files() {
    info "Installing MacDaddy application files to ${INSTALL_ROOT}"
    install -d -m 0755 "${INSTALL_ROOT}"
    install -m 0755 "${SOURCE_SCRIPT}" "${INSTALL_SCRIPT}"

    prepare_command_path
    info "Creating global command: ${COMMAND_PATH}"
    ln -sfn "${INSTALL_SCRIPT}" "${COMMAND_PATH}"
    chmod 0755 "${INSTALL_SCRIPT}"

    info "Preparing system backup directory: ${BACKUP_DIR}"
    install -d -m 0755 "${BACKUP_DIR}"
}

print_summary() {
    cat <<EOF_SUMMARY

MacDaddy installation complete.

Run interactive mode:
  sudo ${APP_NAME}

Useful CLI commands:
  ${APP_NAME} --help
  sudo ${APP_NAME} list
  sudo ${APP_NAME} backup
  sudo ${APP_NAME} randomize <interface>

Installed files:
  Application: ${INSTALL_SCRIPT}
  Command:     ${COMMAND_PATH}
  Backups:     ${BACKUP_DIR}/mac_backup.txt

To uninstall MacDaddy later:
  sudo ./uninstall.sh
EOF_SUMMARY
}

main() {
    require_root
    require_source
    install_dependencies
    verify_dependencies
    install_files
    success "MacDaddy is ready."
    print_summary
}

main "$@"
