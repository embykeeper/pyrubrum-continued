# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from os import listdir
from shutil import copyfile

import pyrubrum

# -- Project information -----------------------------------------------------

project = pyrubrum.__package__
copyright = "2020, Hearot"
author = pyrubrum.__author__

root_files = ["CHANGELOG.md", "CODE_OF_CONDUCT.md", "README.md", "SECURITY.md"]
copies = root_files + ["FEATURES.md"]

for root_file in root_files:
    copyfile("../../" + root_file, root_file)

for root_file in copies:
    copyfile("../../" + root_file, "_static/" + root_file)

for example in filter(lambda f: f.endswith(".py"), listdir("../../examples")):
    copyfile("../../examples/" + example, "_static/examples/" + example)

copyfile("../../examples/sample.env", "_static/examples/sample.env")

with open("README.md", "r", encoding="utf-8") as readme:
    content = readme.read().replace("./", "_static/")

with open("README.md", "w", encoding="utf-8") as readme:
    readme.write(content)

# The full version, including alpha/beta/rc tags
release = pyrubrum.__version__

napoleon_include_init_with_doc = False

# -- General configuration ---------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

default_role = "py:obj"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "m2r",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_favicon = "_static/assets/icon.ico"

html_logo = "_static/assets/mark_logo.png"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {"style_nav_header_background": "pink"}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {
    "pyrogram": ("https://docs.pyrogram.org/", None),
    "python": ("https://docs.python.org/3", None),
    "redis": ("https://redis-py.readthedocs.io/en/stable/", None),
}
