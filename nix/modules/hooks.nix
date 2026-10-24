{ inputs, ... }:
{
  imports = [ inputs.hooks.flakeModule ];

  perSystem =
    { pkgs, ... }:
    {
      pre-commit.settings.hooks = {
        deadnix.enable = true;
        nixfmt.enable = true;
        ruff.enable = true;
        ruff-format.enable = true;
        statix.enable = true;
      };

      pagelens.devShell.buildInputs = with pkgs; [
        deadnix
        nixfmt
        pre-commit
        ruff
        statix
      ];

      formatter = pkgs.nixfmt-tree;
    };
}
