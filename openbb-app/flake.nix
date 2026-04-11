{
  description = "OpenBB financial app";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          pip
          virtualenv
          setuptools
          wheel
          # streamlit removed here — managed by pip inside venv instead
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
            pkgs.libffi
            pkgs.openssl
            pkgs.ruff
          ];
          shellHook = ''
            unset PYTHONPATH
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH

            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
            fi

            source .venv/bin/activate

            # Remove pip-installed ruff and symlink Nix's ruff into venv instead
            rm -f .venv/bin/ruff
            ln -sf ${pkgs.ruff}/bin/ruff .venv/bin/ruff

            if ! python -c "import openbb" 2>/dev/null; then
              echo "Installing OpenBB..."
              pip install --upgrade pip
              pip install "openbb==1.6.7" "openbb-yfinance==1.6.0" streamlit plotly
              # Remove pip's ruff again after install and relink Nix's
              rm -f .venv/bin/ruff
              ln -sf ${pkgs.ruff}/bin/ruff .venv/bin/ruff
            fi

            export PATH="$PWD/.venv/bin:$PATH"
            echo "OpenBB dev environment ready!"
          '';
        };
      });
}