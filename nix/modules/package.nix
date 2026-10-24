_: {
  perSystem =
    { pkgs, ... }:
    {
      packages.default = pkgs.python312Packages.buildPythonApplication {
        pname = "pagelens";
        version = "0.1.0";
        src = ../..;
        pyproject = true;

        build-system = [ pkgs.python312Packages.hatchling ];
        dependencies = with pkgs.python312Packages; [
          numpy
          pillow
          pydantic
          pymupdf
          rich
          typer
        ];

        nativeCheckInputs = with pkgs.python312Packages; [
          pytestCheckHook
          pytest-cov
        ];
        pythonImportsCheck = [ "pagelens" ];
        meta.mainProgram = "pagelens";
      };
    };
}
