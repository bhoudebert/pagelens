_: {
  perSystem =
    { pkgs, ... }:
    let
      python = pkgs.python312.withPackages (
        ps: with ps; [
          mypy
          numpy
          pillow
          pydantic
          pymupdf
          pytest
          pytest-cov
          rich
          typer
        ]
      );
    in
    {
      _module.args.pagelensPython = python;
      pagelens.devShell.buildInputs = [ python ];
    };
}
