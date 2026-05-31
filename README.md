<img width="1881" height="836" alt="macdaddyMAINbnr" src="https://github.com/user-attachments/assets/8f12a6cc-e592-41f2-9d73-a96d837ab82b" />

# MacDaddy

**MacDaddy** is a WastelandSYS Linux terminal utility for managing network interface MAC addresses with an interactive menu, scriptable CLI commands, backup/restore support, and automation-friendly workflows.

It is built for practical Linux administration, Raspberry Pi labs, Kali/Debian systems, and authorized network testing where you need MAC address changes to be readable, reversible, and easy to run from the terminal.

---

# WHY MACDADDY?

Changing a MAC address by hand often means stitching together `ip`, `macchanger`, interface state changes, notes, and backup files. MacDaddy keeps that work in one focused tool without hiding what is happening.

MacDaddy is designed to:

* Inspect MAC-capable interfaces before changes are made.
* Randomize, reset, or assign MAC addresses through guided prompts or CLI commands.
* Back up current MAC/interface state so changes can be restored later.
* Keep risky operations clear, especially when a change may disconnect SSH, Wi-Fi, VPN, or other active sessions.
* Stay lightweight enough for Raspberry Pi and lab systems while still feeling polished beside other WastelandSYS utilities.

MacDaddy is a MAC address management utility, not a bypass or abuse tool. Use it only on systems and networks where you have permission to make interface changes.

---

# FEATURES

* WastelandSYS-style interactive terminal menu.
* Automation-friendly CLI mode.
* Terminal-width aware banner and menu centering.
* List available MAC-capable network interfaces.
* Show MAC address and interface details for a selected interface.
* Randomize one interface or every detected MAC-capable interface.
* Reset one interface or all interfaces to their permanent MAC addresses through `macchanger`.
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
* Installer for `/opt/macdaddy` plus the global `macdaddy` command.
* Uninstaller that removes installed launchers and application files while preserving backups.
* GPLv3 licensed.

---

# MACDADDY WORKFLOW

### Main Menu

<p align="center">
<img width="638" height="490" alt="macdaddyMAINMENU" src="https://github.com/user-attachments/assets/83730df6-355a-46cd-a35f-8a16c99f94ce" />
</p>

Access MAC randomization, custom MAC assignment, backup, restore, automation, and interface management from a single terminal interface.

### Interface Detection

<p align="center">
<img width="641" height="330" alt="macdaddyINTERFACESELECTION" src="https://github.com/user-attachments/assets/c4301fc7-117c-4b47-ab8d-b284b96acbfb" />
</p>

Detect and display MAC-capable network interfaces before performing MAC address operations.

### Randomize MAC Address

<p align="center">
<img width="641" height="344" alt="macdaddyRANDOMIZED" src="https://github.com/user-attachments/assets/9b2b8ec1-aed8-4ad4-acda-a1246e52066d" />
</p>

Generate and apply randomized MAC addresses through a guided workflow for quick identity changes.

### Backup

<p align="center">
<img width="641" height="244" alt="macdaddyBACKUP1" src="https://github.com/user-attachments/assets/806bc7b9-6c13-45a4-a2fa-e43e33462375" />
</p>

Create backups of current MAC address settings before making changes or running automated workflows.

### Restore

<p align="center">
<img width="609" height="359" alt="macdaddyBACKUPRESTORED1" src="https://github.com/user-attachments/assets/b5d92fba-b29e-420a-99fc-68415587b812" />
</p>

Restore previously saved MAC address configurations and recover original adapter settings.

### Automation Mode
<p align="center">
<img width="561" height="484" alt="macdaddyAUTOMATEDCHANGES" src="https://github.com/user-attachments/assets/b3ce4965-85fc-4a60-9558-68d98039bad9" />
</p>

Continuously randomize MAC addresses at configurable intervals while displaying current, permanent, and newly assigned addresses.

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

* Check that it is running with root privileges.
* Install required packages on apt-based systems when `apt-get` is available.
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

The uninstaller removes installed MacDaddy launchers and application files:

* `/usr/local/bin/macdaddy`
* `/opt/macdaddy`
* MacDaddy desktop entries if any were installed later

The uninstaller intentionally does **not** remove user backups or user-created data, including files under `/var/lib/macdaddy`, `~/.local/share/macdaddy`, custom backup paths, or local backup files.

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

Target platforms:

* Kali Linux
* Debian
* Ubuntu
* Raspberry Pi OS
* Raspberry Pi / ARM Linux environments

Expected to work on other Linux distributions when these commands are available:

* `python3`
* `ip` from `iproute2`
* `macchanger`

Notes:

* MAC changes usually require root privileges.
* Changing MAC addresses can disconnect SSH, Wi-Fi, VPN, or other active network sessions.
* Some drivers, virtual interfaces, managed networks, or Wi-Fi environments may prevent MAC changes.
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

# LICENSE

MacDaddy is released under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for the full license text.

---

# AUTHOR

[WastelandSYS](https://github.com/WastelandSYS)
