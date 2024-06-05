{
  description = "Manage tmuxp session configurations";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
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
      };

      python = pkgs."python${pythonVersion}";

      inherit (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;}) mkPoetryApplication mkPoetryEnv;
    in {
      packages = {
        ${projectName} = mkPoetryApplication {
          inherit python projectDir;

          preferWheels = true;
        };

        default = self.packages.${system}.${projectName};
      };

      devShells = {
        ${projectName} = mkPoetryEnv {
          inherit python projectDir;

          preferWheels = true;
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
