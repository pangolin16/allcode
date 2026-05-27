{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (ps: with ps; [
      flask
    ]))
  ];

  shellHook = ''
    echo "Python environment with Flask is ready!"
  '';
}