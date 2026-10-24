_: {
  perSystem =
    {
      config,
      pagelensPython,
      pkgs,
      ...
    }:
    {
      pagelens.devShell.buildInputs = with pkgs; [
        git
        gnumake
        jq
        ollama
        sqlite
        tesseract
        uv
      ];

      devShells.default = pkgs.mkShell {
        name = "pagelens-shell";
        packages = config.pagelens.devShell.buildInputs;
        env = {
          UV_PYTHON = pkgs.python312.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          # Other modules pull in their own Python and PYTHONPATH; pin ours.
          export PYTHONPATH="$PWD/src"
          export PATH="${pagelensPython}/bin:$PATH"
          ${config.pre-commit.installationScript}
          echo "pagelens development shell"
          echo "Run 'python -m pagelens.cli --help' or 'make quality'."
        '';
      };
    };
}
