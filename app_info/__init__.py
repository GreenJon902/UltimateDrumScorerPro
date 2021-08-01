import appdirs

name = "UltimateDrumScorerPro"
name_short = 'UDSP'
author = "GreenJon902"
version = "ALPHA_1.0.1"

description = f"{name} is a new drum scorer or sheet music writing program made by {author}. You are using version "\
              f"{version}"

dirs = appdirs.AppDirs(appname=name, appauthor=author, version=version)


__all__ = ["name", "author", "version", "dirs", "description", "name_short"]
