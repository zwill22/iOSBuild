import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "iOSBuild"
copyright = "2025, Z M Williams"
author = "Z M Williams"

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "myst_parser"
]

autodoc_typehints = 'description'

autodoc_member_order = "bysource"

napoleon_google_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

html_theme = "sphinx_rtd_theme"

html_context = {
    "display_github": True,
    "github_user": "zwill22",
    "github_repo": "iOSBuild",
    "conf_py_path": "/docs/",
    "github_version": "main"
}

autosectionlabel_prefix_document = True
