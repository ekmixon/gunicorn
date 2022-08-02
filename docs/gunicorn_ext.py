import os
import inspect

from docutils import nodes, utils

import gunicorn.config as guncfg

HEAD = """\
.. Please update gunicorn/config.py instead.

.. _settings:

Settings
========

This is an exhaustive list of settings for Gunicorn. Some settings are only
able to be set from a configuration file. The setting name is what should be
used in the configuration file. The command line arguments are listed as well
for reference on setting at the command line.

.. note::

    Settings can be specified by using environment variable
    ``GUNICORN_CMD_ARGS``. All available command line arguments can be used.
    For example, to specify the bind address and number of workers::

        $ GUNICORN_CMD_ARGS="--bind=127.0.0.1 --workers=3" gunicorn app:app

    .. versionadded:: 19.7

"""
ISSUE_URI = 'https://github.com/benoitc/gunicorn/issues/%s'
PULL_REQUEST_URI = 'https://github.com/benoitc/gunicorn/pull/%s'


def format_settings(app):
    settings_file = os.path.join(app.srcdir, "settings.rst")
    ret = []
    known_settings = sorted(guncfg.KNOWN_SETTINGS, key=lambda s: s.section)
    for i, s in enumerate(known_settings):
        if i == 0 or s.section != known_settings[i - 1].section:
            ret.append("%s\n%s\n\n" % (s.section, "-" * len(s.section)))
        ret.append(fmt_setting(s))

    with open(settings_file, 'w') as settings:
        settings.write(HEAD)
        settings.write(''.join(ret))


def fmt_setting(s):
    if callable(s.default):
        val = inspect.getsource(s.default)
        val = "\n".join(f"    {line}" for line in val.splitlines())
        val = "\n\n.. code-block:: python\n\n" + val
    elif s.default == '':
        val = "``''``"
    else:
        val = "``%r``" % s.default

    if s.cli and s.meta:
        cli = " or ".join(f"``{arg} {s.meta}``" for arg in s.cli)
    elif s.cli:
        cli = " or ".join(f"``{arg}``" for arg in s.cli)
    else:
        cli = ""

    out = [".. _%s:\n" % s.name.replace("_", "-")]
    out.append(f"``{s.name}``")
    out.extend(("~" * (len(s.name) + 4), ""))
    if s.cli:
        out.extend((f"**Command line:** {cli}", ""))
    out.extend((f"**Default:** {val}", ""))
    out.extend((s.desc, "", ""))
    return "\n".join(out)


def issue_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    issue = utils.unescape(text)
    text = f'issue {issue}'
    refnode = nodes.reference(text, text, refuri=ISSUE_URI % issue)
    return [refnode], []


def pull_request_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    issue = utils.unescape(text)
    text = f'pull request {issue}'
    refnode = nodes.reference(text, text, refuri=PULL_REQUEST_URI % issue)
    return [refnode], []


def setup(app):
    app.connect('builder-inited', format_settings)
    app.add_role('issue', issue_role)
    app.add_role('pr', pull_request_role)
