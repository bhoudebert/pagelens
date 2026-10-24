#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$root/testdata/sources"
output_dir="$root/testdata/manuals"
profile_dir="$(mktemp -d)"
trap 'rm -rf "$profile_dir"' EXIT
mkdir -p "$output_dir"

render() {
  local source="$1"
  local output="$2"
  chromium \
    --headless \
    --disable-gpu \
    --disable-crash-reporter \
    --disable-breakpad \
    --no-sandbox \
    --user-data-dir="$profile_dir" \
    --allow-file-access-from-files \
    --no-pdf-header-footer \
    --print-to-pdf="$output_dir/$output" \
    "file://$source_dir/$source"
}

render pump_catalog.html pump-catalog.pdf
render service_bulletin.html service-bulletin.pdf
render vehicle_catalog.html vehicle-catalog.pdf
render image_only_scan.html image-only-scan.pdf

echo "Generated manuals in $output_dir"

