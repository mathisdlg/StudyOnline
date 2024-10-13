{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShellNoCC {
    packages = with pkgs;[
        redis
        (python3.withPackages (python-pkgs: with python-pkgs; [
            redis
            django
            django-redis
            django-debug-toolbar
        ]))
    ];

    LANG = "";
    LC_COLLATE = "C";
    LC_CTYPE = "UTF-8";
    LC_MESSAGES = "C";
    LC_MONETARY = "C";
    LC_NUMERIC = "C";
    LC_TIME = "C";

    shellHook = ''
        python manage.py runserver &
    '';
}