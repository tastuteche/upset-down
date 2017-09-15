# -*- coding: utf-8 -*-
import re
import os
import click

SETUP_PY_TEMPLATE = """# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='%(name)s',
    version=%(version)s,
    packages=find_packages(),
    include_package_data=%(include_package_data)s,
    install_requires=[%(install_requires)s],
)
"""
from stdlib_list import stdlib_list
libraries = stdlib_list("3.4")
libraries.append('setuptools')
STDLIB_MODULES = set(libraries)


IMPORT_RES = [
    re.compile(r'^\s*import\s+(?P<package>[a-zA-Z0-9_]+)'),
    re.compile(r'^\s*from\s+(?P<package>[a-zA-Z0-9_]+)'),
]

VERSION_RE = re.compile(r'^__version__\s=', re.M)


def guess_dependencies_from_file(path, ignore):
    with open(path) as fobj:
        data = fobj.readlines()
    names = set()
    for l in data:
        for regex in IMPORT_RES:
            names.update(regex.findall(l))
    return [name for name in names if name.split('.')[0] not in ignore]


def guess_dependencies(projectdir):
    dependencies = set()
    base_ignore = [guess_name(projectdir)]
    for root, _, filenames in os.walk(projectdir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(root, filename)
                dependencies.update(guess_dependencies_from_file(
                    path, base_ignore + [filename[:-3] for filename in filenames if filename.endswith('.py')]))
    return ','.join(['"%s"' % name for name in dependencies if name not in STDLIB_MODULES])


def find_package_data(projectdir):
    package_data = []
    parent = guess_name(projectdir)
    for name in ['templates', 'locale', 'static']:
        if os.path.exists(os.path.join(projectdir, name)):
            package_data.append('recursive-include %s/%s *' % (parent, name))
    return '\n'.join(package_data)


def guess_name(projectdir):
    return os.path.basename(os.path.realpath(projectdir.rstrip('/')))


def guess_version(projectdir):
    with open(os.path.join(projectdir, '__init__.py')) as fobj:
        data = fobj.read()
    if VERSION_RE.search(data):
        return '__import__("%s").__version__' % guess_name(projectdir)
    else:
        return '"1.0"'


@click.command()
@click.argument('projectdir')
def main(projectdir):
    if not os.path.exists(projectdir):
        print("No project not found at %s" % projectdir)
        return
    package_data = find_package_data(projectdir)
    context = {
        'name': guess_name(projectdir),
        'version': guess_version(projectdir),
        'include_package_data': 'True' if package_data else 'False',
        'name': guess_name(projectdir),
        'install_requires': guess_dependencies(projectdir),
    }

    setup_py_path = os.path.join(projectdir, 'setup.py')
    if not os.path.exists(setup_py_path):
        with open(setup_py_path, 'w') as fobj:
            fobj.write(SETUP_PY_TEMPLATE % context)
    else:
        print("%s already exists!" % setup_py_path)

    MANIFEST_in_path = os.path.join(projectdir, 'MANIFEST.in')
    if not os.path.exists(MANIFEST_in_path):
        if package_data:
            with open(MANIFEST_in_path, 'w') as fobj:
                fobj.write(package_data)
    else:
        print("%s already exists!" % MANIFEST_in_path)


if __name__ == '__main__':
    main()
