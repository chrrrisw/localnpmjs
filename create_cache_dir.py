import os

USERDIR = os.path.expanduser('~')
NPMDIR = os.path.join(USERDIR, '.npm')
CACHEDIR = os.path.join(USERDIR, 'offline_npm')

for dirpath, dirnames, filenames in os.walk(top=NPMDIR):
    if 'package.tgz' in filenames:
        tarball_source = os.path.join(dirpath, 'package.tgz')

        try:
            name, version = os.path.relpath(dirpath, NPMDIR).split(os.sep)
        except ValueError as e:
            print('#############ERROR', dirpath, e)
            name1, name2, version = os.path.relpath(dirpath, NPMDIR).split(os.sep)
            name = '{}%2f{}'.format(name1, name2)
            print('#############trying', name)

        tarball_name = '{}-{}.tgz'.format(name, version)
        tarball_destination = os.path.join(CACHEDIR, tarball_name)
        # print()
        if os.path.exists(tarball_destination):
            print('# Not copying', tarball_name, tarball_source)
        else:
            print('cp -i {} {}'.format(
                tarball_source,
                tarball_destination))
