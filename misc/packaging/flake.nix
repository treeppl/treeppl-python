{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treeppl.url = "github:treeppl/treeppl?dir=misc/packaging";
    treeppl.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, treeppl }:
    let
      mkPkg = system:
        let
          pkgs = nixpkgs.legacyPackages.${system}.pkgs;
          tpkgs = treeppl.packages.${system};
        in
          rec {
            packages.treeppl-python = pkgs.callPackage ./treeppl-python.nix {
              inherit (tpkgs) tpplc-tmp-tar-gz;
            };
          };
    in flake-utils.lib.eachDefaultSystem mkPkg;
}
