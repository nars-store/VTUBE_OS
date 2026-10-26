#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID="$ROOT/vtube-connect/android"
if [[ ! -d "$ANDROID" ]]; then echo "Android project not found: $ANDROID"; exit 2; fi
if command -v gradle >/dev/null 2>&1; then
  cd "$ANDROID"
  gradle --no-daemon assembleDebug
  APK="$ANDROID/app/build/outputs/apk/debug/app-debug.apk"
  if [[ -f "$APK" ]]; then mkdir -p "$ROOT/build-output"; cp "$APK" "$ROOT/build-output/VTUBE-Connect-debug.apk"; echo "APK ready: $ROOT/build-output/VTUBE-Connect-debug.apk"; else echo "Gradle ran but APK not found."; exit 3; fi
else
  echo "Gradle is not installed. Open vtube-connect/android in Android Studio (JDK 17 + Android SDK 35), sync Gradle, then Build > Build APK(s)."
  exit 1
fi
