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

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }: let
    projectDir = self;
    project = nixpkgs.lib.importTOML "${projectDir}/pyproject.toml";
    projectName = project.tool.poetry.name;
    pythonVersion = "311";
  in
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;

        overlays = [
          poetry2nix.overlay
        ];
      };

      inherit (pkgs.poetry2nix) mkPoetryApplication mkPoetryEnv;

      python = pkgs."python${pythonVersion}";

      overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
        mypy = super.mypy.overridePythonAttrs (old: {
          enableParallelBuilding = true;
        });

        # workaround https://github.com/nix-community/poetry2nix/issues/568
        tmuxp = super.tmuxp.overridePythonAttrs (old: {
          buildInputs = (old.buildInputs or []) ++ [self.poetry-core];
        });
      });
    in {
      packages = {
        ${projectName} = mkPoetryApplication {
          inherit python projectDir overrides;
        };

        default = self.packages.${system}.${projectName};
      };

      devShells = {
        ${projectName} = mkPoetryEnv {
          inherit python projectDir overrides;
        };

        default = pkgs.mkShell {
          packages = [
            pkgs.poetry
            self.devShells.${system}.${projectName}
          ];
        };
      };
    });
}
