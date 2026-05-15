#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time

# ANSI color codes. They are disabled automatically for non-interactive output
# unless --color is explicitly requested.
RESET = "\033[0m"
HEADER = "\033[96m"
TEXT = "\033[93m"
INFO = "\033[94m"
SUCCESS = "\033[92m"
WARNING = "\033[93m"
ERROR = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

APP_NAME = "macdaddy"
DEFAULT_BACKUP_FILE = "mac_backup.txt"
MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
AUTO_CHANGE_THREAD = None
AUTO_CHANGE_STOP = threading.Event()
USE_COLOR = sys.stdout.isatty()
DRY_RUN = False


class MacDaddyError(Exception):
    """Raised for expected command and validation failures."""


def colorize(message, color):
    if not USE_COLOR:
        return message
    return f"{color}{message}{RESET}"


def print_color(message, color=TEXT):
    print(colorize(message, color))


def clear_terminal():
    if sys.stdout.isatty():
        os.system("clear")


def print_header():
    print(colorize("\n" + "=" * 50, HEADER))
    print(colorize("           ╭━╮╭━╮╱╱╱╱╱╭━━━╮╱╱╱╱╭╮╱╭╮", HEADER))
    print(colorize("           ┃┃╰╯┃┃╱╱╱╱╱╰╮╭╮┃╱╱╱╱┃┃╱┃┃", HEADER))
    print(colorize("           ┃╭╮╭╮┣━━┳━━╮┃┃┃┣━━┳━╯┣━╯┣╮╱╭╮", HEADER))
    print(colorize("           ┃┃┃┃┃┃╭╮┃╭━╯┃┃┃┃╭╮┃╭╮┃╭╮┃┃╱┃┃", HEADER))
    print(colorize("           ┃┃┃┃┃┃╭╮┃╰━┳╯╰╯┃╭╮┃╰╯┃╰╯┃╰━╯┃", HEADER))
    print(colorize("           ╰╯╰╯╰┻╯╰┻━━┻━━━┻╯╰┻━━┻━━┻━╮╭╯", HEADER))
    print(colorize("           ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━╯┃", HEADER))
    print(colorize("           ╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━━╯", HEADER))
    print(colorize("=" * 50 + "\n", HEADER))


def default_backup_path():
    override = os.environ.get("MACDADDY_BACKUP_FILE")
    if override:
        return Path(override).expanduser()

    if os.geteuid() == 0:
        return Path("/var/lib") / APP_NAME / DEFAULT_BACKUP_FILE

    data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(data_home).expanduser() if data_home else Path.home() / ".local" / "share"
    return base / APP_NAME / DEFAULT_BACKUP_FILE


def resolve_backup_path(path=None, prefer_existing_legacy=False):
    if path:
        return Path(path).expanduser()

    backup_path = default_backup_path()
    legacy_path = Path.cwd() / DEFAULT_BACKUP_FILE
    if prefer_existing_legacy and legacy_path.exists() and not backup_path.exists():
        return legacy_path
    return backup_path


def run_cmd(args, check=True, root=False, dry_run=False):
    """Run a command with captured output and consistent errors."""
    command_text = " ".join(args)
    if dry_run or DRY_RUN:
        print_color(f"[dry-run] {command_text}", INFO)
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    if root and os.geteuid() != 0:
        raise MacDaddyError(f"Root privileges are required. Re-run with: sudo {' '.join(sys.argv)}")

    try:
        result = subprocess.run(
            args,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise MacDaddyError(f"Required command not found: {args[0]}") from exc

    if check and result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise MacDaddyError(f"Command failed: {command_text}\n{details}")
    return result


def require_command(command):
    if shutil.which(command) is None:
        raise MacDaddyError(f"Required command not found: {command}")


def require_root():
    if os.geteuid() != 0 and not DRY_RUN:
        raise MacDaddyError(f"Root privileges are required. Re-run with: sudo {' '.join(sys.argv)}")


def load_interface_data():
    """Return interface data from iproute2 JSON output."""
    result = run_cmd(["ip", "-j", "link", "show"])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise MacDaddyError("Could not parse interface data from `ip -j link show`.") from exc


def normalize_mac(mac):
    return mac.strip().lower()


def is_valid_mac(mac):
    mac = normalize_mac(mac)
    if not MAC_RE.match(mac):
        return False, "MAC address must use format XX:XX:XX:XX:XX:XX."
    octets = [int(part, 16) for part in mac.split(":")]
    if all(octet == 0 for octet in octets):
        return False, "MAC address cannot be all zeroes."
    if octets[0] & 1:
        return False, "MAC address cannot be multicast; the first octet must be even."
    return True, ""


def is_locally_administered(mac):
    return bool(int(normalize_mac(mac).split(":")[0], 16) & 2)


def interface_records(include_loopback=False):
    records = []
    for item in load_interface_data():
        name = item.get("ifname")
        if not name:
            continue
        flags = item.get("flags", [])
        if not include_loopback and "LOOPBACK" in flags:
            continue
        address = item.get("address", "")
        valid, _ = is_valid_mac(address) if address else (False, "")
        if not valid:
            continue
        records.append(
            {
                "name": name,
                "mac": normalize_mac(address),
                "state": item.get("operstate", "UNKNOWN"),
                "flags": flags,
                "type": item.get("link_type", "unknown"),
            }
        )
    return records


def get_interfaces():
    return [record["name"] for record in interface_records()]


def get_interface_record(interface):
    for record in interface_records(include_loopback=True):
        if record["name"] == interface:
            return record
    raise MacDaddyError(f"Invalid interface name: {interface}")


def interface_is_up(interface):
    record = get_interface_record(interface)
    return "UP" in record.get("flags", [])


def validate_interface(interface):
    return get_interface_record(interface)["name"]


def set_interface_state(interface, state, dry_run=False):
    validate_interface(interface)
    if state not in {"up", "down"}:
        raise MacDaddyError("Interface state must be 'up' or 'down'.")
    require_root()
    run_cmd(["ip", "link", "set", interface, state], root=True, dry_run=dry_run)
    print_color(f"Interface {interface} has been set to {state}.", SUCCESS)


def run_with_interface_down(interface, action, dry_run=False):
    """Bring interface down for action, then restore previous state when possible."""
    validate_interface(interface)
    was_up = interface_is_up(interface)
    require_root()
    down_ok = False
    try:
        run_cmd(["ip", "link", "set", interface, "down"], root=True, dry_run=dry_run)
        down_ok = True
        return action()
    finally:
        if down_ok and was_up:
            try:
                run_cmd(["ip", "link", "set", interface, "up"], check=False, root=True, dry_run=dry_run)
            except MacDaddyError as exc:
                print_color(f"[warning] Could not bring {interface} back up: {exc}", WARNING)


def randomize_mac(interface, dry_run=False):
    validate_interface(interface)
    require_command("macchanger")

    def action():
        result = run_cmd(["macchanger", "-r", interface], root=True, dry_run=dry_run)
        if result.stdout:
            print_color(result.stdout.rstrip(), SUCCESS)

    run_with_interface_down(interface, action, dry_run=dry_run)


def reset_mac(interface, dry_run=False):
    validate_interface(interface)
    require_command("macchanger")

    def action():
        result = run_cmd(["macchanger", "-p", interface], root=True, dry_run=dry_run)
        if result.stdout:
            print_color(result.stdout.rstrip(), SUCCESS)

    run_with_interface_down(interface, action, dry_run=dry_run)


def set_custom_mac(interface, new_mac, dry_run=False):
    validate_interface(interface)
    new_mac = normalize_mac(new_mac)
    valid, reason = is_valid_mac(new_mac)
    if not valid:
        raise MacDaddyError(reason)
    if not is_locally_administered(new_mac):
        print_color(
            "Warning: this is not a locally administered MAC. Consider setting the second-least-significant bit of the first octet.",
            WARNING,
        )

    def action():
        run_cmd(["ip", "link", "set", interface, "address", new_mac], root=True, dry_run=dry_run)
        print_color(f"MAC address for {interface} changed to {new_mac}.", SUCCESS)

    run_with_interface_down(interface, action, dry_run=dry_run)


def show_interfaces():
    records = interface_records()
    if not records:
        print_color("No interfaces found.", WARNING)
        return

    print_color("\nAvailable Interfaces:", INFO)
    print(f"{'Interface':<20} {'MAC Address':<20} {'State':<12} {'Type':<10}")
    print(colorize("-" * 68, HEADER))
    for record in records:
        print(f"{record['name']:<20} {record['mac']:<20} {record['state']:<12} {record['type']:<10}")


def show_mac_addresses(interface):
    validate_interface(interface)
    print_color(f"Showing MAC address information for {interface}...\n", INFO)

    if shutil.which("macchanger"):
        result = run_cmd(["macchanger", "-s", interface], check=False)
        if result.returncode == 0 and result.stdout:
            print_color(result.stdout.rstrip(), SUCCESS)
        else:
            print_color(result.stderr.strip() or f"Could not retrieve macchanger data for {interface}.", WARNING)
    else:
        print_color("macchanger is not installed; showing iproute2 details only.", WARNING)

    result = run_cmd(["ip", "addr", "show", interface], check=False)
    if result.returncode == 0:
        print_color("\nAdditional Interface Information:", INFO)
        print(result.stdout.rstrip())
    else:
        print_color(result.stderr.strip() or f"Could not retrieve details for {interface}.", ERROR)


def backup_mac_addresses(path=None):
    records = interface_records()
    if not records:
        print_color("No interfaces found to back up.", WARNING)
        return

    backup_path = resolve_backup_path(path)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    with backup_path.open("w", encoding="utf-8") as file:
        file.write("# MacDaddy MAC address backup\n")
        file.write(f"# Created: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        for record in records:
            file.write(f"{record['name']} {record['mac']}\n")
    print_color(f"MAC addresses backed up to {backup_path}.", SUCCESS)


def read_backup(path=None):
    backup_path = resolve_backup_path(path, prefer_existing_legacy=True)
    if not backup_path.exists():
        raise MacDaddyError(f"Backup file not found: {backup_path}")

    entries = []
    with backup_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 2:
                raise MacDaddyError(f"Invalid backup line {line_number}: {line}")
            interface, mac = parts
            valid, reason = is_valid_mac(mac)
            if not valid:
                raise MacDaddyError(f"Invalid MAC on backup line {line_number}: {reason}")
            entries.append((interface, normalize_mac(mac)))
    return backup_path, entries


def restore_mac_addresses(path=None, dry_run=False):
    backup_path, entries = read_backup(path)
    if not entries:
        print_color(f"Backup file has no MAC entries: {backup_path}", WARNING)
        return

    current_interfaces = set(get_interfaces())
    for interface, mac in entries:
        if interface not in current_interfaces:
            print_color(f"Skipping missing interface from backup: {interface}", WARNING)
            continue
        set_custom_mac(interface, mac, dry_run=dry_run)
    print_color(f"Restore completed from {backup_path}.", SUCCESS)


def check_interface_status(interface):
    record = get_interface_record(interface)
    flags = ",".join(record["flags"])
    print_color(f"Interface {interface} is {record['state']} with flags [{flags}].", INFO)


def randomize_all(dry_run=False):
    interfaces = get_interfaces()
    if not interfaces:
        print_color("No interfaces found.", WARNING)
        return
    for interface in interfaces:
        print_color(f"\nRandomizing {interface}...", INFO)
        try:
            randomize_mac(interface, dry_run=dry_run)
        except MacDaddyError as exc:
            print_color(f"[ERROR] {exc}", ERROR)


def reset_all(dry_run=False):
    interfaces = get_interfaces()
    if not interfaces:
        print_color("No interfaces found.", WARNING)
        return
    for interface in interfaces:
        print_color(f"\nResetting {interface}...", INFO)
        try:
            reset_mac(interface, dry_run=dry_run)
        except MacDaddyError as exc:
            print_color(f"[ERROR] {exc}", ERROR)


def confirm(prompt, default=False):
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{prompt} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def auto_change_mac_addresses(interval, interfaces=None, dry_run=False):
    targets = interfaces or get_interfaces()
    if not targets:
        print_color("No interfaces found.", WARNING)
        return

    while not AUTO_CHANGE_STOP.is_set():
        for interface in targets:
            if AUTO_CHANGE_STOP.is_set():
                break
            try:
                print_color(f"\nAuto-randomizing {interface}...", INFO)
                randomize_mac(interface, dry_run=dry_run)
            except MacDaddyError as exc:
                print_color(f"[ERROR] {exc}", ERROR)
        AUTO_CHANGE_STOP.wait(interval)


def start_auto_change(interval, interfaces=None, dry_run=False):
    global AUTO_CHANGE_THREAD
    if AUTO_CHANGE_THREAD is not None and AUTO_CHANGE_THREAD.is_alive():
        print_color("Automatic MAC address changing is already running.", WARNING)
        return
    if interval <= 0:
        raise MacDaddyError("Interval must be a positive integer.")

    AUTO_CHANGE_STOP.clear()
    AUTO_CHANGE_THREAD = threading.Thread(
        target=auto_change_mac_addresses,
        args=(interval, interfaces, dry_run),
        daemon=True,
    )
    AUTO_CHANGE_THREAD.start()
    print_color(f"Automatic MAC address changing started with an interval of {interval} seconds.", SUCCESS)


def stop_auto_change_mac():
    global AUTO_CHANGE_THREAD
    if AUTO_CHANGE_THREAD is None or not AUTO_CHANGE_THREAD.is_alive():
        print_color("Automatic MAC address changing is not running.", WARNING)
        return

    print_color("Stopping automatic MAC changing...", INFO)
    AUTO_CHANGE_STOP.set()
    AUTO_CHANGE_THREAD.join(timeout=5)
    if AUTO_CHANGE_THREAD.is_alive():
        print_color("Automatic MAC changing is still stopping; please wait a moment.", WARNING)
    else:
        print_color("Automatic MAC address changing has stopped.", SUCCESS)


def prompt_interface():
    records = interface_records()
    if not records:
        raise MacDaddyError("No interfaces found.")

    print_color("Available interfaces:", INFO)
    for index, record in enumerate(records, start=1):
        print(f"{index}. {record['name']} ({record['mac']}, {record['state']})")

    choice = input("Enter interface name or number: ").strip()
    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(records):
            return records[index - 1]["name"]
    return validate_interface(choice)


def menu_action(action):
    try:
        action()
    except MacDaddyError as exc:
        print_color(f"[ERROR] {exc}", ERROR)
    except ValueError as exc:
        print_color(f"[ERROR] Invalid value: {exc}", ERROR)


def main_menu():
    while True:
        clear_terminal()
        print_header()
        print_color("      MacDaddy - MAC Address Changer - v1.2", INFO)
        print(colorize("=" * 50, HEADER))
        print_color("1.  Show available interfaces")
        print_color("2.  Show MAC address information")
        print_color("3.  Randomize MAC address of an interface")
        print_color("4.  Randomize MAC addresses of all interfaces")
        print_color("5.  Reset MAC address of an interface")
        print_color("6.  Reset MAC addresses of all interfaces")
        print_color("7.  Backup MAC addresses")
        print_color("8.  Restore MAC addresses from backup")
        print_color("9.  Set custom MAC address")
        print_color("10. Check interface status")
        print_color("11. Start auto MAC address changing")
        print_color("12. Stop auto MAC address changing")
        print_color("13. Change interface state (up/down)")
        print_color("14. Exit")
        print(colorize("=" * 50, HEADER))

        choice = input("Enter your choice: ").strip()
        clear_terminal()
        print_header()

        if choice == "1":
            menu_action(show_interfaces)
        elif choice == "2":
            menu_action(lambda: show_mac_addresses(prompt_interface()))
        elif choice == "3":
            menu_action(lambda: randomize_mac(prompt_interface()))
        elif choice == "4":
            if confirm("This can disconnect network sessions. Continue?"):
                menu_action(randomize_all)
        elif choice == "5":
            menu_action(lambda: reset_mac(prompt_interface()))
        elif choice == "6":
            if confirm("This can disconnect network sessions. Continue?"):
                menu_action(reset_all)
        elif choice == "7":
            menu_action(backup_mac_addresses)
        elif choice == "8":
            if confirm("Restoring MACs can disconnect network sessions. Continue?"):
                menu_action(restore_mac_addresses)
        elif choice == "9":
            def set_custom_from_menu():
                interface = prompt_interface()
                new_mac = input("Enter the new MAC address (format: XX:XX:XX:XX:XX:XX): ").strip()
                set_custom_mac(interface, new_mac)
            menu_action(set_custom_from_menu)
        elif choice == "10":
            menu_action(lambda: check_interface_status(prompt_interface()))
        elif choice == "11":
            def start_from_menu():
                interval = int(input("Enter interval between changes in seconds: "))
                start_auto_change(interval)
            menu_action(start_from_menu)
        elif choice == "12":
            menu_action(stop_auto_change_mac)
        elif choice == "13":
            def state_from_menu():
                interface = prompt_interface()
                state = input("Enter desired state (up/down): ").strip().lower()
                set_interface_state(interface, state)
            menu_action(state_from_menu)
        elif choice == "14":
            if AUTO_CHANGE_THREAD is not None and AUTO_CHANGE_THREAD.is_alive():
                stop_auto_change_mac()
            clear_terminal()
            break
        else:
            print_color("Invalid choice. Please try again.", ERROR)

        input("\nPress Enter to go back...")


def build_parser():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Manage, randomize, back up, and restore network interface MAC addresses.",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")
    parser.add_argument("--color", action="store_true", help="Force colored output.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without changing interfaces.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("menu", help="Launch the interactive menu.")
    subparsers.add_parser("list", help="List available interfaces.")

    show = subparsers.add_parser("show", help="Show MAC details for one interface.")
    show.add_argument("interface")

    randomize = subparsers.add_parser("randomize", help="Randomize one interface's MAC address.")
    randomize.add_argument("interface")

    randomize_all_parser = subparsers.add_parser("randomize-all", help="Randomize all detected MAC-capable interfaces.")
    randomize_all_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")

    reset = subparsers.add_parser("reset", help="Reset one interface to its permanent MAC address.")
    reset.add_argument("interface")

    reset_all_parser = subparsers.add_parser("reset-all", help="Reset all detected MAC-capable interfaces.")
    reset_all_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")

    set_parser = subparsers.add_parser("set", help="Set one interface to a custom MAC address.")
    set_parser.add_argument("interface")
    set_parser.add_argument("mac")

    status = subparsers.add_parser("status", help="Show one interface's status.")
    status.add_argument("interface")

    state = subparsers.add_parser("state", help="Set one interface up or down.")
    state.add_argument("interface")
    state.add_argument("state", choices=["up", "down"])

    backup = subparsers.add_parser("backup", help="Back up current MAC addresses.")
    backup.add_argument("--file", help="Backup file path. Defaults to ~/.local/share/macdaddy/mac_backup.txt.")

    restore = subparsers.add_parser("restore", help="Restore MAC addresses from backup.")
    restore.add_argument("--file", help="Backup file path. Defaults to ~/.local/share/macdaddy/mac_backup.txt.")
    restore.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")

    auto = subparsers.add_parser("auto", help="Randomize MAC addresses repeatedly until Ctrl+C.")
    auto.add_argument("--interval", type=int, required=True, help="Seconds between randomization runs.")
    auto.add_argument("interfaces", nargs="*", help="Interfaces to randomize. Defaults to all detected interfaces.")

    return parser


def run_cli(args):
    if args.command in {None, "menu"}:
        main_menu()
    elif args.command == "list":
        show_interfaces()
    elif args.command == "show":
        show_mac_addresses(args.interface)
    elif args.command == "randomize":
        randomize_mac(args.interface, dry_run=args.dry_run)
    elif args.command == "randomize-all":
        if args.yes or confirm("This can disconnect network sessions. Continue?"):
            randomize_all(dry_run=args.dry_run)
    elif args.command == "reset":
        reset_mac(args.interface, dry_run=args.dry_run)
    elif args.command == "reset-all":
        if args.yes or confirm("This can disconnect network sessions. Continue?"):
            reset_all(dry_run=args.dry_run)
    elif args.command == "set":
        set_custom_mac(args.interface, args.mac, dry_run=args.dry_run)
    elif args.command == "status":
        check_interface_status(args.interface)
    elif args.command == "state":
        set_interface_state(args.interface, args.state, dry_run=args.dry_run)
    elif args.command == "backup":
        backup_mac_addresses(args.file)
    elif args.command == "restore":
        if args.yes or confirm("Restoring MACs can disconnect network sessions. Continue?"):
            restore_mac_addresses(args.file, dry_run=args.dry_run)
    elif args.command == "auto":
        if args.interval <= 0:
            raise MacDaddyError("Interval must be a positive integer.")
        interfaces = args.interfaces or None
        if interfaces:
            for interface in interfaces:
                validate_interface(interface)
        print_color("Press Ctrl+C to stop automatic MAC changing.", INFO)
        try:
            auto_change_mac_addresses(args.interval, interfaces=interfaces, dry_run=args.dry_run)
        except KeyboardInterrupt:
            AUTO_CHANGE_STOP.set()
            print_color("\nAutomatic MAC changing stopped.", SUCCESS)


def main(argv=None):
    global USE_COLOR, DRY_RUN
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        USE_COLOR = False
    elif args.color:
        USE_COLOR = True
    DRY_RUN = args.dry_run

    try:
        run_cli(args)
    except MacDaddyError as exc:
        print_color(f"[ERROR] {exc}", ERROR)
        return 1
    except ValueError as exc:
        print_color(f"[ERROR] Invalid value: {exc}", ERROR)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
