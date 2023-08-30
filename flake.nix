{
  description = "Manage tmuxp session configurations";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/23.05";
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
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
      poetry2nix = pkgs.poetry2nix;
    in {
      packages = {
        ${projectName} = poetry2nix.mkPoetryApplication {
          inherit python projectDir;

          preferWheels = true;
        };

        default = self.packages.${system}.${projectName};
      };

      devShells = {
        ${projectName} = poetry2nix.mkPoetryEnv {
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
