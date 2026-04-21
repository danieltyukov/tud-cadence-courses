#!/bin/bash
# Launch Cadence Virtuoso on ET4382 server via RDP (xrdp)
# ET4382 uses a full remote desktop (xrdp) rather than ssh X11 forwarding.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED_FILE="${SCRIPT_DIR}/password_ET4382.txt"

NETID=$(grep '^login:'    "$CRED_FILE" | awk '{print $2}')
PASSWORD=$(grep '^password:' "$CRED_FILE" | awk '{print $2}')
SERVER=$(grep '^server:'   "$CRED_FILE" | awk '{print $2}')

if ! command -v xfreerdp3 >/dev/null && ! command -v xfreerdp >/dev/null; then
    notify-send "Cadence ET4382" "xfreerdp is not installed. Run: sudo apt install freerdp3-x11" 2>/dev/null
    echo "ERROR: xfreerdp not found. Install with: sudo apt install freerdp3-x11" >&2
    exit 1
fi

RDP=$(command -v xfreerdp3 || command -v xfreerdp)

# Remote framebuffer is a fixed, xrdp-friendly resolution (1920x1080 is
# supported by every xrdp version). /smart-sizing decouples the local
# window size from the framebuffer so the window manager can resize and
# snap the window freely (Super+Left/Right, tiling, etc.) — the framebuffer
# just scales to fit.
exec "$RDP" \
    /v:"$SERVER" \
    /u:"$NETID" \
    /p:"$PASSWORD" \
    /cert:ignore \
    /sec:rdp \
    /bpp:16 \
    +clipboard \
    /size:1920x1080 \
    /smart-sizing \
    -wallpaper \
    -themes \
    -menu-anims \
    -window-drag \
    /title:"Cadence ET4382 (${SERVER})"
