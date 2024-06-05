{
  description = "Manage tmuxp session configurations";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = {
    self,
    flake-utils,
    nixpkgs,
  }: let
    pyproject = nixpkgs.lib.importTOML "${self}/pyproject.toml";
    project = pyproject.project;
  in
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      pkg = pkgs.python3.pkgs.callPackage ./default.nix {};
    in {
      packages = {
        ${project.name} = pkg;
        default = pkg;
      };
    });
}
