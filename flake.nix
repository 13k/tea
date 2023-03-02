{
  description = "Manage tmuxp session configurations";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    let
      projectDir = self;
      project = nixpkgs.lib.importTOML "${projectDir}/pyproject.toml";
      projectName = project.tool.poetry.name;
      pythonVersion = "310";
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;

          overlays = [
            poetry2nix.overlay
          ];
        };

        python = pkgs."python${pythonVersion}";
        pythonPackages = pkgs."python${pythonVersion}Packages";

        poetryOverrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          # workaround https://github.com/nix-community/poetry2nix/issues/568
          tmuxp = super.tmuxp.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry-core ];
          });
        });
      in
      rec {
        packages =
          {
            ${projectName} = pkgs.poetry2nix.mkPoetryApplication {
              inherit projectDir python;

              overrides = poetryOverrides;
            };

            default = packages.${projectName};
          };

        devShells =
          {
            ${projectName} = pkgs.poetry2nix.mkPoetryEnv {
              inherit projectDir python;

              overrides = poetryOverrides;
            };

            default = pkgs.mkShell {
              packages = [
                pkgs.poetry
                devShells.${projectName}
              ];
            };
          };
      });
}
