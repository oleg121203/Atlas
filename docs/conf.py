# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from unittest.mock import MagicMock

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../core"))
sys.path.insert(0, os.path.abspath("../ui"))
sys.path.insert(0, os.path.abspath("../tools"))
sys.path.insert(0, os.path.abspath("../workflow"))
sys.path.insert(0, os.path.abspath("../intelligence"))
sys.path.insert(0, os.path.abspath("../utils"))
sys.path.insert(0, os.path.abspath("../plugins"))


# Mock problematic imports for documentation building
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "psutil",
    "pyautogui",
    "selenium",
    "google",
    "google.auth",
    "google.auth.transport",
    "google.auth.transport.requests",
    "googleapiclient",
    "googleapiclient.discovery",
    "Quartz",
    "AppKit",
    "Foundation",
]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# -- Project information -----------------------------------------------------
project = "Atlas AI Assistant"
copyright = "2025, Atlas Development Team"
author = "Atlas Development Team"
release = "2.0.0"
version = "2.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
]

# MyST Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_static_path = ["_static"]
html_logo = "../assets/icon.png"
html_favicon = "../assets/icon.icns"

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyside6": ("https://doc.qt.io/qtforpython/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Autodoc configuration ---------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_mock_imports = MOCK_MODULES

# Napoleon configuration for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# -- Options for HTML output -------------------------------------------------
