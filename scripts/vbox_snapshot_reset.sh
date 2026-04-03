#!/usr/bin/env bash
set -euo pipefail
VM_NAME="${1:-WinSandbox}"
SNAPSHOT="${2:-CleanState}"

VBoxManage controlvm "$VM_NAME" poweroff || true
VBoxManage snapshot "$VM_NAME" restore "$SNAPSHOT"
