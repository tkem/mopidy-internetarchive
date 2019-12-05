import configparser
import pathlib


def setup(app):
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )


def get_version():
    # Get current library version without requiring the library to be
    # installed, like ``pkg_resources.get_distribution(...).version`` requires.
    cp = configparser.ConfigParser()
    cp.read(pathlib.Path(__file__).parent.parent / "setup.cfg")
    return cp["metadata"]["version"]


project = "Mopidy-InternetArchive"
copyright = "2014-2019 Thomas Kemmer"
version = get_version()
release = version

exclude_patterns = ["_build"]
master_doc = "index"
html_theme = "default"

latex_documents = [
    (
        "index",
        "Mopidy-InternetArchive.tex",
        "Mopidy-InternetArchive Documentation",
        "Thomas Kemmer",
        "manual",
    )
]

man_pages = [
    (
        "index",
        "mopidy-internetarchive",
        "Mopidy-InternetArchive Documentation",
        ["Thomas Kemmer"],
        1,
    )
]
