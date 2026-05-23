import importlib.metadata


project = "Mopidy-InternetArchive"
copyright = "2014-2026 Thomas Kemmer"
release = importlib.metadata.version(project)
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]
exclude_patterns = ["_build"]
master_doc = "index"
html_theme = "classic"
