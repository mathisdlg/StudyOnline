{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShellNoCC {
    packages = with pkgs;[
        redis
        python3
        python3Packages.pip
    ];

    LANG = "";
    LC_COLLATE = "C";
    LC_CTYPE = "UTF-8";
    LC_MESSAGES = "C";
    LC_MONETARY = "C";
    LC_NUMERIC = "C";
    LC_TIME = "C";

    shellHook = ''
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        redis-server &
        python manage.py runserver
    '';
}