# -*- coding: utf-8 -*-
import itcase_sphinx_theme

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo'
]

intersphinx_mapping = {
    'http://sacrud.readthedocs.org/en/master': None,
}

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'ps_alchemy'
copyright = u'2016, uralbash'

# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

#  -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'itcase'

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [itcase_sphinx_theme.get_html_themes_path()]

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = 'PS_ALCHEMY'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'ps_alchemydoc'

html_theme_options = {
    'travis_button': True,
    'github_button': True,
    'github_user': 'sacrud',
    'github_repo': 'ps_alchemy',
}
