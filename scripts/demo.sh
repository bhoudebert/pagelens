#!/usr/bin/env bash
# End-to-end Pagelens demo on the synthetic manuals in testdata/.
# Usage: scripts/demo.sh            (retrieval only)
#        scripts/demo.sh --verify   (adds vision-model confirmation)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

data_dir="${PAGELENS_DEMO_DIR:-.pagelens-demo}"
verify=()
[[ "${1:-}" == "--verify" ]] && verify=(--verify)

run_pagelens() {
  if command -v pagelens >/dev/null 2>&1; then
    command pagelens "$@"
  else
    PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}" python -m pagelens "$@"
  fi
}

step() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

if ! curl -fsS "${PAGELENS_OLLAMA_URL:-http://127.0.0.1:11434}/api/version" >/dev/null; then
  echo "Ollama is not reachable. Start it with 'ollama serve' and pull the models:" >&2
  echo "  ollama pull embeddinggemma-2:440m-q8_0-text-vision" >&2
  echo "  ollama pull qwen3-vl:8b-instruct" >&2
  exit 1
fi

step "1/4  Create a fresh collection in $data_dir"
rm -rf "$data_dir"
run_pagelens init --data-dir "$data_dir"

step "2/4  Index four synthetic manuals"
run_pagelens ingest testdata/manuals --data-dir "$data_dir"
run_pagelens status --data-dir "$data_dir"

step "3/4  Where is a water pump shown?"
run_pagelens query "water pump" --limit 5 --data-dir "$data_dir" "${verify[@]}"

step "4/4  Score the pipeline against page-level ground truth"
run_pagelens evaluate testdata/ground-truth.json --data-dir "$data_dir" "${verify[@]}"
