#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

inputs_jq='.locks.nodes.root.inputs | keys | .[]'
metadata_json="$(nix flake metadata --json)"
inputs_str="$(jq -r "$inputs_jq" <<<"$metadata_json")"

readarray -t inputs <<<"$inputs_str"

update_inputs_args=()

for input in "${inputs[@]}"; do
	update_inputs_args+=("--update-input" "$input")
done

exec nix flake lock "${update_inputs_args[@]}"
