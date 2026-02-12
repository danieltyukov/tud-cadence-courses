# Cadence Virtuoso Setup Documentation

## Overview

This directory contains the setup for launching Cadence Virtuoso on a remote server (`ee4610.ewi.tudelft.nl`) with automatic authentication and local file synchronization.

## System Architecture

```
Local Machine                          Remote Server (ee4610.ewi.tudelft.nl)
─────────────                          ────────────────────────────────────
├── Desktop Entry                      ├── ~/tsmcBCD/
│   (Application Menu)                 │   ├── .cdsinit
│   └─> launch-cadence.sh              │   ├── sourceme
│       ├─> mount-tsmcBCD.sh          │   ├── cds.lib
│       │   (Auto-sync local folder)   │   ├── assura_tech.lib
│       └─> SSH + Launch Virtuoso      │   └── [Design files]
│                                      │
├── tsmcBCD/ (Local Mirror)            └── Cadence Virtuoso
│   └─> [Real-time sync via sshfs]         (Running on server,
│                                            displayed via X11)
└── password_username.txt
    (Credentials)
```

## Files and Their Purposes

### Configuration Files

#### `password_username.txt`
Stores SSH credentials for automatic authentication:
```
login:     datyukov
password:  haimahkemiele
```

**Security Note**: This file contains sensitive credentials. Keep it secure and don't share it.

### Scripts

#### `launch-cadence.sh`
Main launcher script that:
1. Reads password from `password_username.txt`
2. Calls `mount-tsmcBCD.sh` to ensure remote directory is mounted
3. Uses `sshpass` to authenticate automatically
4. Connects via SSH with X11 forwarding (`ssh -X`)
5. Navigates to `tsmcBCD` directory on remote server
6. Sources the environment setup (`source sourceme`)
7. Launches Cadence Virtuoso (`virtuoso &`)

**Location**: `/home/danieltyukov/workspace/tud/tud-digital-ic-design/launch-cadence.sh`

#### `mount-tsmcBCD.sh`
Mounts the remote `tsmcBCD` directory locally using sshfs:
- **Local mount point**: `./tsmcBCD/`
- **Remote directory**: `datyukov@ee4610.ewi.tudelft.nl:tsmcBCD`
- **Features**:
  - Automatic password authentication
  - Auto-reconnect on connection loss
  - Keep-alive to maintain connection
  - Follows symlinks

**Options used**:
- `password_stdin`: Accept password from stdin
- `reconnect`: Auto-reconnect if connection drops
- `ServerAliveInterval=15`: Send keep-alive every 15 seconds
- `ServerAliveCountMax=3`: Max failed keep-alives before disconnect
- `follow_symlinks`: Follow symbolic links on remote

#### `unmount-tsmcBCD.sh`
Safely unmounts the synced directory:
```bash
./unmount-tsmcBCD.sh
```

Use this when:
- You're done working and want to disconnect
- The mount becomes unresponsive
- You need to remount the directory

### Desktop Entry

#### `~/.local/share/applications/cadence-virtuoso.desktop`
Desktop application entry that appears in the application menu:
- **Name**: Cadence Virtuoso
- **Icon**: `candence.png` (from this directory)
- **Execution**: Calls `launch-cadence.sh`
- **Terminal**: Runs without visible terminal window
- **Category**: Development > Electronics

## Directory Structure

```
/home/danieltyukov/workspace/tud/tud-digital-ic-design/
├── CADENCE-SETUP.md              # This documentation
├── password_username.txt          # SSH credentials
├── launch-cadence.sh              # Main launcher script
├── mount-tsmcBCD.sh               # Mount script for sync
├── unmount-tsmcBCD.sh             # Unmount script
├── candence.png                   # Application icon
├── tsmcBCD/                       # Local mirror of remote directory
│   ├── .cdsinit                   # Cadence initialization
│   ├── sourceme                   # Environment setup
│   ├── cds.lib                    # Library definitions
│   ├── assura_tech.lib           # Technology library
│   └── [Your design files]        # Created when you work
└── CalibreSetup/                  # Initial setup files
```

## How to Use

### Launching Cadence

**Method 1: Application Menu (Recommended)**
1. Open your application menu
2. Search for "Cadence Virtuoso"
3. Click to launch
4. Cadence will open automatically (no password prompt)

**Method 2: Command Line**
```bash
cd /home/danieltyukov/workspace/tud/tud-digital-ic-design
./launch-cadence.sh
```

### Working with Files

All your Cadence work is automatically synced:
- **Remote work**: Any files created/modified in Cadence appear locally in `./tsmcBCD/`
- **Local access**: Access your design files locally for backup, version control, etc.
- **Real-time sync**: Changes are reflected immediately in both directions

### Manual Mount/Unmount

**Mount manually**:
```bash
./mount-tsmcBCD.sh
```

**Unmount manually**:
```bash
./unmount-tsmcBCD.sh
```

**Check if mounted**:
```bash
mountpoint tsmcBCD
# or
mount | grep tsmcBCD
```

## Remote Server Details

- **Server**: `ee4610.ewi.tudelft.nl`
- **Username**: `datyukov` (your netid)
- **Working directory**: `~/tsmcBCD`
- **Technology**: TSMC 180nm BCD (tsmc18)
- **Environment setup**: `sourceme` script must be sourced before launching Cadence

### Important Cadence Notes

1. **Library linking**: When creating libraries, link them to `tsmc18`
2. **Transistor models**: Use `nmos2v`, `nmos5v`, `pmos2v`, `pmos5v` for oscillators and TDC
3. **License warnings**: Click "OK" or "Always" when opening schematics and ADE
4. **Configuration files**:
   - `.cdsinit`: Cadence initialization settings
   - `sourceme`: Sets up TSMC 180nm technology environment variables

## Dependencies

The following software must be installed:

1. **sshpass**: For automatic SSH password authentication
   ```bash
   sudo apt-get install sshpass
   ```

2. **sshfs**: For mounting remote directory locally
   ```bash
   sudo apt-get install sshfs
   ```

3. **SSH with X11**: For graphical forwarding (usually pre-installed)

4. **Alacritty**: Set as default terminal emulator
   ```bash
   sudo update-alternatives --set x-terminal-emulator /usr/local/bin/alacritty
   ```

## Troubleshooting

### Cadence doesn't launch
1. Check if you can SSH manually:
   ```bash
   ssh -X datyukov@ee4610.ewi.tudelft.nl
   ```
2. Verify password in `password_username.txt` is correct
3. Check if sshpass is installed: `which sshpass`

### Mount fails
1. Check if already mounted: `mountpoint tsmcBCD`
2. If stuck, unmount first: `./unmount-tsmcBCD.sh`
3. Check network connection to server
4. Verify sshfs is installed: `which sshfs`

### Directory appears empty after mount
1. Unmount: `./unmount-tsmcBCD.sh`
2. Verify remote directory exists:
   ```bash
   ssh datyukov@ee4610.ewi.tudelft.nl "ls -la tsmcBCD"
   ```
3. Remount: `./mount-tsmcBCD.sh`

### Mount becomes unresponsive
1. Force unmount: `fusermount -uz tsmcBCD`
2. Remount: `./mount-tsmcBCD.sh`

### Desktop entry doesn't appear
1. Update desktop database:
   ```bash
   update-desktop-database ~/.local/share/applications
   ```
2. Log out and log back in
3. Verify file exists:
   ```bash
   ls -la ~/.local/share/applications/cadence-virtuoso.desktop
   ```

### X11 forwarding not working
1. Check if X11 forwarding is enabled in SSH config
2. Verify `DISPLAY` variable is set:
   ```bash
   echo $DISPLAY
   ```
3. Test X11: `ssh -X datyukov@ee4610.ewi.tudelft.nl "xeyes"`

## Making Changes

### Update Password
Edit `password_username.txt`:
```bash
nano password_username.txt
```

### Change Server or Username
Edit all three scripts:
1. `launch-cadence.sh`
2. `mount-tsmcBCD.sh`

Update these variables:
```bash
SERVER="ee4610.ewi.tudelft.nl"
NETID="datyukov"
```

### Change Icon
Replace `candence.png` with your preferred icon, or update the desktop entry:
```bash
nano ~/.local/share/applications/cadence-virtuoso.desktop
# Change the Icon= line
```

Then update the desktop database:
```bash
update-desktop-database ~/.local/share/applications
```

### Disable Auto-Mount
Edit `launch-cadence.sh` and comment out the mount line:
```bash
# "${SCRIPT_DIR}/mount-tsmcBCD.sh"
```

### Use Different Local Directory
Edit `mount-tsmcBCD.sh` and change:
```bash
LOCAL_DIR="${SCRIPT_DIR}/tsmcBCD"  # Change this path
```

## Security Considerations

1. **Password Storage**: The password is stored in plain text in `password_username.txt`
   - Consider setting up SSH key authentication for better security
   - Keep file permissions restrictive: `chmod 600 password_username.txt`

2. **SSH Key Setup** (Alternative to password):
   ```bash
   ssh-keygen -t ed25519
   ssh-copy-id datyukov@ee4610.ewi.tudelft.nl
   ```
   Then remove password authentication from scripts.

3. **Network Security**: Connection is encrypted via SSH, but ensure you're on a trusted network

## Backup Recommendations

Since `tsmcBCD/` is a live mount, consider:
1. Regular backups of your design files
2. Using git for version control:
   ```bash
   cd tsmcBCD
   git init
   git add .
   git commit -m "Initial commit"
   ```

## References

- **Course**: EE4610 Digital IC Design
- **Technology**: TSMC 180nm BCD
- **Documentation**: `EE4610_Instruction_Manual_2025.pdf`
- **Server**: ee4610.ewi.tudelft.nl

## Quick Command Reference

```bash
# Launch Cadence
./launch-cadence.sh

# Mount remote directory
./mount-tsmcBCD.sh

# Unmount remote directory
./unmount-tsmcBCD.sh

# Check mount status
mountpoint tsmcBCD

# View remote files
ls -la tsmcBCD/

# SSH to server manually
ssh -X datyukov@ee4610.ewi.tudelft.nl

# Update desktop database
update-desktop-database ~/.local/share/applications
```

---

**Last Updated**: 2025-11-29
**Setup by**: Claude Code Assistant
