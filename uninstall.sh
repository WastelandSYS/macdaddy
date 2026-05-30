#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="macdaddy"
INSTALL_ROOT="/opt/${APP_NAME}"
INSTALL_SCRIPT="${INSTALL_ROOT}/macdaddy.py"
COMMAND_PATH="/usr/local/bin/${APP_NAME}"
DESKTOP_FILES=(
    "/usr/share/applications/${APP_NAME}.desktop"
    "/usr/local/share/applications/${APP_NAME}.desktop"
)

info() { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
success() { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

require_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        fail "Please run as root: sudo ./uninstall.sh"
    fi
}

remove_command() {
    if [[ -L "${COMMAND_PATH}" ]]; then
        info "Removing command symlink: ${COMMAND_PATH}"
        rm -f "${COMMAND_PATH}"
    elif [[ -f "${COMMAND_PATH}" ]]; then
        if cmp -s "${COMMAND_PATH}" "${INSTALL_SCRIPT}" 2>/dev/null || grep -q "MacDaddy" "${COMMAND_PATH}" 2>/dev/null; then
            info "Removing legacy installed command: ${COMMAND_PATH}"
            rm -f "${COMMAND_PATH}"
        else
            warn "Leaving ${COMMAND_PATH} untouched because it is not a MacDaddy symlink."
        fi
    fi
}

remove_application_files() {
    if [[ -d "${INSTALL_ROOT}" ]]; then
        info "Removing installed application directory: ${INSTALL_ROOT}"
        rm -rf "${INSTALL_ROOT}"
    fi
}

remove_desktop_entries() {
    local desktop_file
    for desktop_file in "${DESKTOP_FILES[@]}"; do
        if [[ -f "${desktop_file}" ]]; then
            info "Removing desktop entry: ${desktop_file}"
            rm -f "${desktop_file}"
        fi
    done
}

main() {
    require_root
    remove_command
    remove_application_files
    remove_desktop_entries
    success "MacDaddy has been uninstalled."
    warn "User backups and generated files were left untouched."
    warn "System backups, if present, remain under /var/lib/${APP_NAME}."
}

main "$@"
