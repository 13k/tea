{
  lib,
  buildPythonPackage,
  hatchling,
  pyyaml,
  tmuxp,
}: let
  pyproject = lib.importTOML "${./.}/pyproject.toml";
  project = pyproject.project;
in
  buildPythonPackage {
    pname = project.name;
    version = project.version;
    pyproject = true;

    src = ./.;

    build-system = [
      hatchling
    ];

    dependencies = [
      pyyaml
      tmuxp
    ];

    meta = with lib; {
      homepage = project.urls.homepage;
      description = project.description;
      license = licenses.mit;
      mainProgram = "tea";
    };
  }
