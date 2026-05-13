#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${USB_WIFI_MONITOR_LOG:-/home/unitree/usb_wifi_motion_monitor.log}"
INTERVAL="${USB_WIFI_MONITOR_INTERVAL:-1}"
WIFI_IFACE="${WIFI_IFACE:-wlan0}"
DOG_IFACE="${DOG_IFACE:-eth0}"
TOP_N="${USB_WIFI_MONITOR_TOP_N:-18}"

mkdir -p "$(dirname "$LOG_FILE")"

echo "===== USB/Wi-Fi motion monitor started at $(date '+%F %T') =====" >> "$LOG_FILE"
echo "interval=${INTERVAL}s wifi_iface=${WIFI_IFACE} dog_iface=${DOG_IFACE}" >> "$LOG_FILE"

if command -v journalctl >/dev/null 2>&1; then
  {
    echo
    echo "===== kernel/network journal follow started at $(date '+%F %T') ====="
  } >> "$LOG_FILE"
  journalctl -k -f -o short-iso 2>/dev/null \
    | grep --line-buffered -Ei 'usb|xusb|xhci|wlan|rtl|rtw|NetworkManager|wpa|disconnect|not responding|dead|reset|timeout|error' \
    >> "$LOG_FILE" &
  JOURNAL_PID=$!
else
  JOURNAL_PID=""
fi

cleanup() {
  if [ -n "${JOURNAL_PID:-}" ]; then
    kill "$JOURNAL_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

i=0
while true; do
  i=$((i + 1))
  {
    echo
    echo "===== poll $(date '+%F %T') ====="
    uptime
    echo "--- link brief ---"
    ip -brief link show "$WIFI_IFACE" 2>&1 || true
    ip -brief addr show "$WIFI_IFACE" 2>&1 || true
    ip -brief link show "$DOG_IFACE" 2>&1 || true
    ip -brief addr show "$DOG_IFACE" 2>&1 || true
    echo "--- wlan sysfs ---"
    for f in operstate carrier dormant mtu speed; do
      if [ -e "/sys/class/net/${WIFI_IFACE}/${f}" ]; then
        printf "%s=" "$f"
        cat "/sys/class/net/${WIFI_IFACE}/${f}" 2>&1 || true
      fi
    done
    echo "--- wlan stats ---"
    for f in rx_bytes rx_packets rx_errors rx_dropped tx_bytes tx_packets tx_errors tx_dropped; do
      if [ -e "/sys/class/net/${WIFI_IFACE}/statistics/${f}" ]; then
        printf "%s=" "$f"
        cat "/sys/class/net/${WIFI_IFACE}/statistics/${f}" 2>&1 || true
      fi
    done
    if command -v iw >/dev/null 2>&1; then
      echo "--- iw link ---"
      iw dev "$WIFI_IFACE" link 2>&1 || true
    fi
    if [ $((i % 10)) -eq 1 ]; then
      echo "--- usb tree ---"
      lsusb -t 2>&1 || true
      echo "--- net device path ---"
      readlink -f "/sys/class/net/${WIFI_IFACE}/device" 2>&1 || true
      readlink -f "/sys/class/net/${DOG_IFACE}/device" 2>&1 || true
    fi
    echo "--- top cpu ---"
    ps -eo pid,stat,pcpu,pmem,rss,cmd --sort=-pcpu | head -n "$TOP_N"
  } >> "$LOG_FILE" 2>&1
  sleep "$INTERVAL"
done
