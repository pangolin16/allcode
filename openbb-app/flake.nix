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
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.stdenv.cc.cc.lib   # needed for some compiled packages
            pkgs.zlib
            pkgs.libffi
            pkgs.openssl
          ];

          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:$LD_LIBRARY_PATH

            # Create venv if it doesn't exist
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
            fi

            source .venv/bin/activate

            # Install OpenBB if not already installed
            if ! python -c "import openbb" 2>/dev/null; then
              echo "Installing OpenBB..."
              pip install --upgrade pip
              pip install openbb openbb-yfinance streamlit plotly
            fi

            echo "OpenBB dev environment ready!"
          '';
        };
      });
}
