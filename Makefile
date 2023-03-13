.DEFAULT_GOAL := all

.PHONY: all
all: build nix-build ## Run default tasks

.PHONY: build
build: ## Build package with poetry
	@poetry build

.PHONY: nix-build
nix-build: ## Build nix flake
	@nix build --no-link --allow-dirty --no-warn-dirty $(if $(DEBUG),"-L")
	@nix path-info -Sh --allow-dirty --no-warn-dirty

.PHONY: nix-check
nix-check: ## Check nix flake
	@nix flake check

.PHONY: nix-update
nix-update: ## Update flake inputs
	@scripts/nix-update.sh

help: ## Shows this usage
	@echo "Makefile"
	@echo ""
	@echo "Usage:"
	@\grep -E '^[a-zA-Z_-]+:.*?## .*$$' "$(MAKEFILE_LIST)" | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  make \033[36m%-30s\033[0m %s.\n", $$1, $$2}'
