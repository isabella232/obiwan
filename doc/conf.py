# -*- coding: utf-8 -*-
#
# desitemplate documentation build configuration file, created by
# sphinx-quickstart on Tue Dec  9 10:43:33 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# obiwan readthedocs home page is
#http://readthedocs.org/projects/obiwan/

import sys
import os
import os.path

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../')) # test dirs
sys.path.insert(0, os.path.abspath('../py')) #pkg

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

try:
    import sphinx.ext.napoleon
    napoleon_extension = 'sphinx.ext.napoleon'
except ImportError:
    try:
        import sphinxcontrib.napoleon
        napoleon_extension = 'sphinxcontrib.napoleon'
        needs_sphinx = '1.2'
    except ImportError:
        needs_sphinx = '1.3'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'nbsphinx',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
    napoleon_extension
]
nbsphinx_execute = 'never'

# Configuration for intersphinx, copied from astropy.
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    # 'python3': ('http://docs.python.org/3/', path.abspath(path.join(path.dirname(__file__), 'local/python3links.inv'))),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    'scipy': ('http://docs.scipy.org/doc/scipy/reference/', None),
    'matplotlib': ('http://matplotlib.org/', None),
    'astropy': ('http://docs.astropy.org/en/stable/', None),
    'h5py': ('http://docs.h5py.org/en/latest/', None)
    }

from glob import glob
def get_rel_path(name):
    d=dict(obiwan='../py/obiwan',
           tests='../tests/')
    for key in ['runmanager','qa','scaling','dplearn']:
        d[key]= '../py/obiwan/'+key
    return d[name]
    # if name == 'obiwan':
    #     d['obiwan']=
    #
    # return dict(tests= ,
    #         ,
    #        qa= '../py/obiwan/qa',
    #        dplearn= '../py/obiwan/dplearn')[name]

def get_rm_modules(name):
    return ['__init__']

import pandas as pd
def get_modules(name):
    #assert(name in ['obiwan','tests','qa','dplearn'])
    rel_path= get_rel_path(name)
    mods=glob(os.path.join(rel_path,"*.py"))
    mods= [(mod.replace('../py/','')
               .replace('../tests/','tests/')
               .replace('.py','')
               .replace('/','.'))
           for mod in mods]
    suffix= (get_rel_path(name).replace('../py/','')
                               .replace('../tests/','tests/')
                               .replace('.py','')
                               .replace('/','.'))
    print('name=%s, suffix=%s' % (name,suffix))
    for key in get_rm_modules(name):
        key= suffix + '.' + key
        print('key=%s' % (key,))
        if not key == 'tests..__init__':
            mods.remove(key)
    return mods


def write_set_of_modules(name_in_code,title_in_api,
                         file_obj):
    """Used by create_api_rst to write the list of
    obiwan.fetch, obiwan.kenobi, ... in api.rst for
    the obiwan module.

    Args:
        name_in_code: ex) obiwan, runmanager, qa
        title_in_api: ex) modules, post processing,
    """
    section=  title_in_api
    section += "\n" + "-"*len(section) + "\n"
    file_obj.write(section+".. autosummary::\n\t:toctree: _autosummary\n\t:template: module.rst\n\n")
    # modules= ['obiwan.common',
    #           'obiwan.draw_radec_color_z',
    #           'obiwan.kenobi']
    modules= get_modules(name_in_code)
    for module in modules:
        file_obj.write("\t" + module + "\n")
    file_obj.write("\n")

def create_api_rst():
    """
    Adapted from: https://github.com/bccp/nbodykit

    Produce a file "modules.rst" that includes an ``autosummary`` directive
    listing all of the modules in nbodykit.

    The ``toctree`` option is set such that the corresponding rst files
    will be auto-generated in ``./_autosummary/*.rst``.
    """
    # current directory
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    output_file = os.path.join(cur_dir, 'api.rst')
    with open(output_file, 'w') as ff:
        title = "API Documentation"
        title += "\n" + "="*len(title) + "\n"
        title = ":orphan:\n\n" + title
        ff.write(title + "\n")
        for name_in_code,title_in_api in [
                ('obiwan','Modules'),
                ('runmanager','Post-Processing'),
                ('qa','Analysis & Plotting'),
                ('scaling','Scaling Tests'),
                ('tests','Tests'),
                ('dplearn','Deep Learning')]:
            write_set_of_modules(name_in_code,title_in_api,ff)
        # write_set_of_modules('tests','Tests',ff)
        # write_set_of_modules('qa','Compute Jobs',ff)
        # write_set_of_modules('dplearn','Deep Learning',ff)

    # make the output directory if it doesn't exist
    #output_path = os.path.join(cur_dir, 'api', '_autosummary')
    #if not os.path.exists(output_path):
    #    os.makedirs(output_path)

def setup(app):
    """
    Credit: https://github.com/bccp/nbodykit

    Setup steps to prepare the docs build.
    """
    # automatically generate api.rst file containing all modules
    # in a autosummary directive listing with 'toctree' option
    create_api_rst()

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
autosummary_generate = True

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'obiwan'
copyright = u'2014-2018, Kaylan Burleigh, John Moustakas'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

__import__(project)
package = sys.modules[project]

# The short X.Y version.
version = package.__version__.split('-', 1)[0]
# The full version, including alpha/beta/rc tags.
release = package.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build','**.ipynb_checkpoints']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = True

# Include functions that begin with an underscore, e.g. _private().
napoleon_include_private_with_doc = True

# This value contains a list of modules to be mocked up. This is useful when
# some external dependencies are not met at build time and break the
# building process.
###########
# Mockup
# autodoc_mock_imports = ['astrometry','tractor','galsim',
#                         'legacypipe','theValidator',
#                         'legacypipe.runbrick','run_brick',
#                         'legacypipe.decam',
#                         'legacypipe.survey',
#                         'astrometry.libkd.spherematch',
#                         'astrometry.util.ttime',
#                         'tractor.psfex',
#                         'tractor.basics',
#                         'tractor.sfd',
#                         'tractor.brightness',
#                         'theValidator.catalogues',
#                         'Tractor', 'PointSource', 'Image',
#                         'NanoMaggies', 'Catalog', 'RaDecPos',
#                         ]
#
# # http://docs.readthedocs.io/en/latest/faq.html
# from unittest.mock import MagicMock
# class Mock(MagicMock):
#     @classmethod
#     def __getattr__(cls, name):
#             return MagicMock()
# MOCK_MODULES = autodoc_mock_imports
# sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
####################

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = 'default'
#html_theme = 'haiku'

import sphinx_rtd_theme
#html_theme = 'sphinx_rtd_theme'
#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
#import juliadoc
#html_theme = 'julia'
#html_theme_path = [juliadoc.get_theme_dir()]
#html_sidebars = juliadoc.default_sidebars()
import sphinx_bootstrap_theme
html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_theme_options = {
    'navbar_title': 'Obiwan',
    'navbar_site_name': 'Pages',
    'navbar_pagenav_name': 'This Page',
    'navbar_fixed_top': 'false',
    'source_link_position': 'none',
    #'bootswatch_theme': 'cosmo',
    #'bootswatch_theme': 'lumen',
    #'bootswatch_theme': 'sandstone',
    'bootswatch_theme': 'spacelab',
    'navbar_links': [
    ("API", "api"),
    ("Tutorials", "tutorials"),
    ("Deep Learning",'deeplearning')
    ],
}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'obiwandoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  ('index', 'obiwan.tex', u'obiwan Documentation',
   u'DESI', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'obiwan', u'obiwan Documentation',
     [u'DESI'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'obiwan', u'obiwan Documentation',
   u'DESI', 'obiwan', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False
