#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/build-output"
DIST="${VTUBE_DIST:-trixie}"
ARCH="${VTUBE_ARCH:-amd64}"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo $0"
  exit 1
fi

for cmd in lb debootstrap mksquashfs xorriso; do
  command -v "$cmd" >/dev/null || {
    echo "Missing build tool: $cmd"
    echo "Install: apt install live-build debootstrap squashfs-tools xorriso"
    exit 1
  }
done

mkdir -p "$OUT"
rm -rf "$BUILD"
mkdir -p "$BUILD"
cd "$BUILD"

# Debian Live configuration: this is a development live image, not a finished
# disk installer. It boots a live desktop and autostarts the VTUBE Control Center.
lb config \
  --mode debian \
  --distribution "$DIST" \
  --architectures "$ARCH" \
  --binary-images iso-hybrid \
  --debian-installer live \
  --archive-areas "main contrib non-free-firmware" \
  --bootappend-live "boot=live components username=vtube hostname=vtube-os locales=id_ID.UTF-8 keyboard-layouts=us" \
  --apt-recommends true \
  --apt-options "--yes"

mkdir -p config/package-lists config/includes.chroot/opt/vtube-os config/includes.chroot/etc/skel/.config/autostart config/includes.chroot/usr/share/applications
cp "$ROOT/config/package-lists/vtube.list.chroot" config/package-lists/vtube.list.chroot
cp "$ROOT/app.py" "$ROOT/vtube_avatar.py" "$ROOT/vtube_live.py" "$ROOT/run.sh" "$ROOT/README.md" config/includes.chroot/opt/vtube-os/
cp -a "$ROOT/packaging" config/includes.chroot/opt/vtube-os/
cp -a "$ROOT/docs" "$ROOT/vtube-connect" "$ROOT/assets" config/includes.chroot/opt/vtube-os/
cp "$ROOT"/packaging/*.desktop config/includes.chroot/usr/share/applications/
chmod 0755 config/includes.chroot/opt/vtube-os/app.py config/includes.chroot/opt/vtube-os/run.sh

cat > config/includes.chroot/etc/skel/.config/autostart/vtube-control-center.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=VTUBE OS Control Center
Comment=VTUBE-first live streaming workspace
Exec=python3 /opt/vtube-os/app.py
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

lb build

ISO="$(find . -maxdepth 1 -type f -name '*.iso' -print -quit)"
if [[ -z "$ISO" ]]; then
  echo "Build finished but no ISO was found in $BUILD"
  exit 2
fi
cp "$ISO" "$OUT/VTUBE-OS-${DIST}-${ARCH}-alpha.iso"
sha256sum "$OUT/VTUBE-OS-${DIST}-${ARCH}-alpha.iso" | tee "$OUT/SHA256SUMS"
echo
echo "ISO ready: $OUT/VTUBE-OS-${DIST}-${ARCH}-alpha.iso"
echo "Test in QEMU first. This development image is not yet a validated installer."
