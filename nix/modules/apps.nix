_: {
  perSystem =
    {
      config,
      pagelensPython,
      lib,
      pkgs,
      ...
    }:
    let
      pythonApp =
        name: command: description:
        let
          app = pkgs.writeShellApplication {
            inherit name;
            runtimeInputs = [
              pagelensPython
              pkgs.ruff
              pkgs.tesseract
            ];
            text = ''
              cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
              export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
              exec python ${command} "$@"
            '';
          };
        in
        {
          type = "app";
          program = lib.getExe app;
          meta.description = description;
        };
    in
    {
      apps = {
        default = {
          type = "app";
          program = lib.getExe config.packages.default;
          meta.description = "Search PDF collections";
        };
        quality = pythonApp "pagelens-quality" "scripts/quality.py" "Run all quality checks";
      };
    };
}
