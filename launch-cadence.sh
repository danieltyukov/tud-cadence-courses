#!/bin/bash
# Launch Cadence Virtuoso on remote server

# SSH connection details
SERVER="ee4610.ewi.tudelft.nl"
NETID="datyukov"

# Get password from file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSWORD=$(grep "^password:" "${SCRIPT_DIR}/password_username.txt" | awk '{print $2}')

# Mount tsmcBCD directory if not already mounted
"${SCRIPT_DIR}/mount-tsmcBCD.sh"

# Connect to server and launch Cadence with automatic authentication
sshpass -p "${PASSWORD}" ssh -X ${NETID}@${SERVER} "setenv LD_LIBRARY_PATH '' && cd tsmcBCD && source sourceme && virtuoso &"
