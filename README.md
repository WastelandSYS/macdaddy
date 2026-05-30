<img width="1881" height="836" alt="macdaddyMAINbnr" src="https://github.com/user-attachments/assets/8f12a6cc-e592-41f2-9d73-a96d837ab82b" />

# MacDaddy

**MacDaddy** is an advanced Linux terminal utility for managing, randomizing, resetting, backing up, and restoring network interface MAC addresses from either an interactive menu or automation-friendly CLI commands.

Built by **WastelandSYS**, MacDaddy keeps the classic Linux utility feel: direct, terminal-first, scriptable, and practical for Raspberry Pi labs, Kali systems, privacy workflows, and network testing environments.

<img width="1050" height="680" alt="MacDaddy terminal interface" src="https://github.com/user-attachments/assets/09217c89-2d8a-48ec-8d59-1119b3b468ed" />

---

# WHY MACDADDY?

MAC addresses are part of how Linux systems identify network interfaces on local networks. During legitimate testing, lab work, privacy practice, Raspberry Pi projects, and system administration, it is often useful to quickly inspect, randomize, reset, or restore those addresses without manually chaining several commands together.

MacDaddy focuses on that workflow:

* **MAC address management** — view interfaces, inspect MAC information, set custom addresses, and change interface state.
* **Randomization** — randomize one interface or every detected MAC-capable interface with safer down/change/up handling.
* **Reset functionality** — restore interfaces to their permanent hardware MAC addresses through `macchanger`.
* **Backup and restore** — save current interface MAC addresses before making changes and restore them later.
* **Automation support** — use CLI commands, `--dry-run`, confirmation bypass flags, and repeated randomization mode for scripts.
* **Linux and Raspberry Pi use cases** — keep network testing and MAC management simple on laptops, single-board computers, Kali boxes, and Debian/Ubuntu-based systems.

MacDaddy is not designed to hide abuse or bypass network rules. Use it responsibly, only on systems and networks where you have authorization.

---

# FEATURES

* Interactive terminal menu with WastelandSYS-style ASCII branding.
* CLI mode for scripting and automation.
* List available MAC-capable network interfaces.
* Show MAC address and interface details for a selected interface.
* Randomize a selected interface MAC address.
* Randomize all detected MAC-capable interfaces.
* Reset a selected interface to its permanent MAC address.
* Reset all detected MAC-capable interfaces.
* Set a custom MAC address with format validation.
* Warn when a custom MAC is not locally administered.
* Check interface status and flags.
* Bring interfaces up or down.
* Back up MAC addresses to a generated backup file.
* Restore MAC addresses from backup.
* Automatic repeated MAC randomization mode.
* `--dry-run` support for safer command review.
* Color output controls with `--color` and `--no-color`.
* Root checks for operations that modify interfaces.
* Modern installer using `/opt/macdaddy` plus a global `macdaddy` command.
* Clean uninstaller that leaves backups and user-created files untouched.
* GPLv3 licensed.

---

# MACDADDY WORKFLOW

The workflow below follows the same terminal-first flow MacDaddy has always used. Replace the placeholders with updated screenshots when preparing the v1.3 GitHub release.

## 1. Main Menu

```text
[ screenshot placeholder: MacDaddy main menu ]
```

Launch the interactive menu with:

```bash
sudo macdaddy
```

## 2. Interface Selection

```text
[ screenshot placeholder: available interfaces and interface prompt ]
```

MacDaddy detects MAC-capable interfaces and lets you select by name or menu number.

## 3. Random MAC Generation

```text
[ screenshot placeholder: randomize interface output ]
```

Randomize a single interface from the menu or with CLI mode:

```bash
sudo macdaddy randomize wlan0
```

## 4. Backup & Restore

```text
[ screenshot placeholder: backup and restore output ]
```

Back up current addresses before changes:

```bash
sudo macdaddy backup
```

Restore later:

```bash
sudo macdaddy restore --yes
```

## 5. Automation Mode

```text
[ screenshot placeholder: auto randomization mode ]
```

Run repeated randomization until stopped:

```bash
sudo macdaddy auto --interval 300 wlan0
```

---

# INSTALLATION

Clone the repository and run the installer:

```bash
git clone https://github.com/WastelandSYS/macdaddy.git
cd macdaddy
chmod +x install.sh uninstall.sh macdaddy.py
sudo ./install.sh
```

The installer will:

* Install required packages on apt-based systems.
* Verify `python3`, `macchanger`, and `ip` are available.
* Install MacDaddy to `/opt/macdaddy/macdaddy.py`.
* Create the global command `/usr/local/bin/macdaddy`.
* Prepare `/var/lib/macdaddy` for root/system backup storage.

After installation:

```bash
macdaddy --help
sudo macdaddy
```

---

# UNINSTALLATION

Run the uninstaller from the cloned repository:

```bash
sudo ./uninstall.sh
```

The uninstaller removes:

* `/opt/macdaddy`
* `/usr/local/bin/macdaddy`
* MacDaddy desktop entries if any were installed later

The uninstaller intentionally leaves user backups and generated files untouched, including backup files under `/var/lib/macdaddy` or user data directories.

---

# USAGE

## Interactive Mode

Start the menu:

```bash
sudo macdaddy
```

Or explicitly launch it:

```bash
sudo macdaddy menu
```

Common interactive actions include:

* Show available interfaces.
* Show MAC address information.
* Randomize one interface.
* Randomize all interfaces.
* Reset one or all interfaces.
* Back up and restore MAC addresses.
* Set a custom MAC address.
* Start or stop automatic MAC changing.
* Change interface state.

## CLI Mode

Show help:

```bash
macdaddy --help
```

Show version:

```bash
macdaddy --version
```

List interfaces:

```bash
sudo macdaddy list
```

Show one interface:

```bash
sudo macdaddy show wlan0
```

Randomize one interface:

```bash
sudo macdaddy randomize wlan0
```

Randomize all interfaces without an interactive confirmation prompt:

```bash
sudo macdaddy randomize-all --yes
```

Reset one interface:

```bash
sudo macdaddy reset wlan0
```

Reset all interfaces:

```bash
sudo macdaddy reset-all --yes
```

Set a custom MAC address:

```bash
sudo macdaddy set wlan0 02:11:22:33:44:55
```

Check interface status:

```bash
sudo macdaddy status wlan0
```

Bring an interface down or up:

```bash
sudo macdaddy state wlan0 down
sudo macdaddy state wlan0 up
```

Back up MAC addresses:

```bash
sudo macdaddy backup
```

Back up to a specific file:

```bash
sudo macdaddy backup --file ./mac_backup.txt
```

Restore from the default backup path:

```bash
sudo macdaddy restore --yes
```

Restore from a specific backup file:

```bash
sudo macdaddy restore --file ./mac_backup.txt --yes
```

Preview commands without changing interfaces:

```bash
sudo macdaddy --dry-run randomize wlan0
```

Run automation mode:

```bash
sudo macdaddy auto --interval 300 wlan0
```

---

# DIRECTORY STRUCTURE

Repository files:

```text
macdaddy/
├── LICENSE          GPLv3 license text
├── README.md        Project documentation
├── install.sh       Installer for Linux systems
├── macdaddy.py      Main MacDaddy application
└── uninstall.sh     Uninstaller for installed files
```

Installed files:

```text
/opt/macdaddy/macdaddy.py       Installed application
/usr/local/bin/macdaddy         Global command symlink
/var/lib/macdaddy/              Root/system backup directory
```

Generated backup locations:

* Root default: `/var/lib/macdaddy/mac_backup.txt`
* User default: `~/.local/share/macdaddy/mac_backup.txt`
* Environment override: `MACDADDY_BACKUP_FILE=/path/to/file`
* CLI override: `macdaddy backup --file /path/to/file`

MacDaddy also supports older local `mac_backup.txt` files during restore when no newer default backup exists.

---

# COMPATIBILITY

MacDaddy is Linux-focused and depends on Linux networking tools.

Tested and targeted platforms:

* Kali Linux
* Debian
* Ubuntu
* Raspberry Pi OS
* Raspberry Pi 4 / ARM Linux environments

Expected to work on other Linux distributions when these commands are available:

* `python3`
* `ip` from `iproute2`
* `macchanger`

Notes:

* MAC changes usually require root privileges.
* Changing MAC addresses can disconnect SSH, Wi-Fi, VPN, or other active network sessions.
* Some drivers, virtual interfaces, enterprise networks, or managed Wi-Fi environments may prevent MAC changes.
* Non-apt distributions can still use MacDaddy after manually installing dependencies.

---

# DEPENDENCIES

Installed automatically on apt-based systems:

```bash
sudo apt-get install -y python3 macchanger iproute2
```

Dependency purpose:

* `python3` — runs MacDaddy.
* `macchanger` — randomizes and resets MAC addresses.
* `iproute2` — lists interfaces and changes interface state/address information.

---

# WHY MACDADDY?

MacDaddy exists because MAC address management should be fast, readable, recoverable, and scriptable without losing the personality of a real Linux terminal tool.

The project philosophy is simple:

* Keep the WastelandSYS identity.
* Preserve practical terminal workflows.
* Avoid unnecessary GUI layers.
* Make dangerous actions obvious.
* Keep backups easy to find.
* Support both hands-on menu use and automation.
* Stay lightweight enough for Raspberry Pi and lab systems.

MacDaddy belongs beside tools like SystemPi, Encryptopi, and noDIFFier as a focused WastelandSYS utility: polished enough for release, simple enough to trust, and direct enough for the terminal.

---

# RELEASE READINESS FOR v1.3

MacDaddy already has a public v1.2 release. This modernization prepares the project for a future **v1.3** release, not a reset to v1.0.

Before publishing v1.3, consider addressing:

* Capture fresh workflow screenshots and replace the README placeholders.
* Test installer and uninstaller on a clean Debian/Ubuntu/Kali virtual machine.
* Test on Raspberry Pi OS or Kali ARM hardware.
* Verify behavior on Wi-Fi and Ethernet interfaces.
* Confirm the GitHub release artifact, if any, matches the committed source.
* Tag the release as `v1.3.0` after final testing.

Recommended release title:

```text
MacDaddy v1.3.0 — Modernized WastelandSYS Release
```

Suggested release notes:

```markdown
## MacDaddy v1.3.0

MacDaddy v1.3.0 modernizes the project for current WastelandSYS repository standards while preserving the existing MAC address management workflow from v1.2.

### Highlights
- Rewritten README with modern project structure, usage examples, compatibility notes, and release guidance.
- Modernized installer with safer shell practices, dependency verification, clear status messages, and `/opt/macdaddy` installation layout.
- Added `uninstall.sh` to remove installed application files, global command links, and desktop entries while preserving backups.
- Added GPLv3 license support and source header.
- Added CLI version reporting.
- Documented backup locations, generated files, and automation usage.

### Notes
- Existing functionality is preserved.
- Root privileges are still required for interface-changing operations.
- Fresh screenshots are recommended before publishing the GitHub release.
```

Recommended GitHub topics/tags:

```text
mac-address, macchanger, linux, raspberry-pi, kali-linux, networking, privacy-tools, terminal, cli, python, iproute2, wastelandsys
```

Recommended short repository description:

```text
Advanced Linux MAC address management utility for randomization, reset, backup, restore, and automation.
```

Recommended About summary:

```text
MacDaddy is a WastelandSYS Linux terminal utility for managing MAC addresses with interactive and CLI workflows, backup/restore support, randomization, reset features, and Raspberry Pi-friendly automation.
```

---

# LICENSE

GNU GPL v3 License

---

# AUTHOR

**WastelandSYS**

Built for Linux terminal users, Raspberry Pi labs, network testing, and responsible MAC address management.
