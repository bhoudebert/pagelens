{
  description = "pagelens: local multimodal search over PDF collections";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    import-tree.url = "github:vic/import-tree";
    hooks.url = "github:cachix/git-hooks.nix";
    hooks.inputs.nixpkgs.follows = "nixpkgs";
  };

  # Dendritic: capabilities are flake-parts modules discovered automatically.
  outputs =
    inputs@{ flake-parts, import-tree, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (import-tree ./nix/modules);
}
