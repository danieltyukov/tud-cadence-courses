#!/bin/bash
# Register a library that was copied into EE4610's ~/tsmcBCD/ by adding a
# DEFINE entry to ~/tsmcBCD/cds.lib on the EE4610 server. Idempotent.
#
# Usage: ./register-library-EE4610.sh LIBNAME [LIBNAME ...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED_FILE="${SCRIPT_DIR}/password_username.txt"
SERVER="ee4610.ewi.tudelft.nl"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 LIBNAME [LIBNAME ...]" >&2
    echo "Example: $0 my_voltage_divider" >&2
    exit 1
fi

NETID=$(grep '^login:'    "$CRED_FILE" | awk '{print $2}')
PASSWORD=$(grep '^password:' "$CRED_FILE" | awk '{print $2}')

# The remote runs tcsh as the login shell, so we base64-encode the bash
# payload and pipe it into bash. This avoids all cross-shell quoting pain.
for LIB in "$@"; do
    echo "=== $LIB ==="
    PAYLOAD=$(cat <<EOF
set -e
LIB='$LIB'
CDS="\$HOME/tsmcBCD/cds.lib"
DIR="\$HOME/tsmcBCD/\$LIB"
if [ ! -d "\$DIR" ]; then
    echo "  MISSING: \$DIR does not exist on $SERVER — scp it from ET4382 first"
    exit 2
fi
if [ ! -f "\$DIR/cdsinfo.tag" ]; then
    echo "  WARNING: \$DIR has no cdsinfo.tag — may not be a valid Cadence library"
fi
if grep -Eq "^DEFINE[[:space:]]+\$LIB[[:space:]]+" "\$CDS"; then
    echo "  already registered in cds.lib"
else
    echo "DEFINE \$LIB \$DIR" >> "\$CDS"
    echo "  added: DEFINE \$LIB \$DIR"
fi
EOF
)
    B64=$(printf '%s' "$PAYLOAD" | base64 -w0)
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=accept-new "$NETID@$SERVER" \
        "echo $B64 | base64 -d | bash" \
        || echo "  FAILED for $LIB"
done

echo
echo "Done. Restart Virtuoso on EE4610 (or run: Tools → Library Manager → File → Refresh) to see the new library."
