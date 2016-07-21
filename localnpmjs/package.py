import tarfile
import json
import os
import re
import uuid
import hashlib
import datetime
from distutils.version import StrictVersion

'''
_attachments
_distfiles
_rev 0-0000000000000000
_uplinks
author
bugs
description
dist-tags {latest}
homepage
keywords
license
maintainers
name
readmeFilename
repository
time {modified}
versions
'''

TARBALL = 'tgz'



def generate_package_json_from_tarball(cache_dir, package_name, tarball_name, server_address):
    tarball_path = os.path.join(cache_dir, tarball_name)
    tarball_stat = os.stat(tarball_path)
    tarball_mtime = datetime.datetime.fromtimestamp(tarball_stat.st_mtime, tz=datetime.timezone.utc).isoformat()
    tarball_ctime = datetime.datetime.fromtimestamp(tarball_stat.st_ctime, tz=datetime.timezone.utc).isoformat()
    tf = tarfile.open(tarball_path)
    package_json = tf.extractfile('package/package.json')
    package_json_str = ''.join([line.decode() for line in package_json])
    package_dict = json.loads(package_json_str)
    tf.close()

    if package_dict['name'] == package_name:
        print('Name matches package_name')

        version = package_dict.get('version', '')

        # Calculate SHA1 sum for tarball
        sha1 = hashlib.sha1()
        with open(tarball_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        author = package_dict.get('author', '')
        if isinstance(author, str) and author != '':
            print('AUTHOR IS STRING', author)
            m = re.match('(.*)<(.*)>', author)
            if m:
                author_name = m.group(1).strip()
                author_email = m.group(2).strip()
            else:
                author_name = author
                author_email = ''
        elif isinstance(author, dict):
            print('AUTHOR IS DICT')
            author_name = author['name']
            author_email = author['email']
        else:
            print('EMPTY AUTHOR ', type(author))
            author_name = ''
            author_email = ''

        description = {}

        description['_attachments'] = {}  # TODO:
        description['_id'] = package_name
        description['_rev'] = '1-{}'.format(uuid.uuid4().hex)  # TODO: Increment number?

        description['author'] = {
            'name': author_name,
            'email': author_email
        }

        description['bugs'] = package_dict.get('bugs', '')
        description['description'] = package_dict.get('description', '')

        description['dist-tags'] = {}
        description['dist-tags']['latest'] = version

        description['homepage'] = package_dict.get('homepage', '')
        description['keywords'] = package_dict.get('keywords', '')
        description['license'] = package_dict.get('license', '')

        description['maintainers'] = [{
            'name': author_name,
            'email': author_email
        }]

        description['name'] = package_name
        description['readmeFilename'] = ''  # TODO:
        description['repository'] = package_dict.get('repository', '')

        description['time'] = {
            'modified': tarball_mtime,
            'created': tarball_ctime,
            'version': tarball_mtime
        }

        description['versions'] = {}
        description['versions'][version] = package_dict
        # TODO
        description['versions'][version]['_from'] = '.'
        description['versions'][version]['_id'] = '{}@{}'.format(package_name, version)
        description['versions'][version]['_nodeVersion'] = '5.7.1'
        description['versions'][version]['_npmOperationalInternal'] = {}
        description['versions'][version]['_npmUser'] = {
            'email': author_email,
            'name': author_name
        }
        description['versions'][version]['_npmVersion'] = '3.6.0'
        description['versions'][version]['_shasum'] = sha1.hexdigest()
        description['versions'][version]['directories'] = {}
        description['versions'][version]['dist'] = {
            'shasum': sha1.hexdigest(),
            'tarball': '{}/{}'.format(server_address, tarball_name)
        }
        description['versions'][version]['gitHead'] = ''
        description['versions'][version]['maintainers'] = [{
            'email': author_email,
            'name': author_name
        }]
        description['versions'][version]['scripts'] = {}

        # TODO: Do we need these?
        description['users'] = {}  # TODO:
        description['readme'] = ''  # TODO:
        description['contributors'] = package_dict.get('contributors', '')

        # Now write the json file.
        if os.path.exists(os.path.join(cache_dir, package_name)):
            print('OVERWRITING')
            with open(os.path.join(cache_dir, package_name), 'w') as f:
                f.write(json.dumps(description, sort_keys=True, indent=4))
        else:
            print('CREATING')
            with open(os.path.join(cache_dir, package_name), 'w') as f:
                f.write(json.dumps(description, sort_keys=True, indent=4))
        return True
    else:
        return False


def get_package_json(cache_dir, package_name, server_address):
    found = False
    for entry in os.listdir(cache_dir):
        if entry.startswith(package_name):
            print('Found matching file:', entry)
            if entry == package_name:
                # We've found our json file
                print('\tIs matching JSON file.')
                found = True
                break  # No need to go any further
            elif entry.endswith(TARBALL):
                # We've found a package tarball that might fit
                print('\tIs matching tarball')
                found = generate_package_json_from_tarball(
                    cache_dir=cache_dir,
                    package_name=package_name,
                    tarball_name=entry,
                    server_address=server_address)

    if found:
        return package_name
    else:
        return None

TARBALL_MATCHER = re.compile('(.*)-([0-9].*).tgz')


class TarballCacher(object):
    def __init__(self, cache_dir, force_new=False):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(self.cache_dir, '.cache')
        if os.path.exists(self.cache_file):
            # read it in
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            # create it
            self.cache = {
                'tarballs': {},
                'packages': {}}
        self._update_cache(force_new=force_new)

    def _write_cache(self):
        print('_write_cache')
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4, sort_keys=True)

    def _update_cache(self, force_new=False):
        print('_update_cache')
        tarballs = [f for f in os.listdir(self.cache_dir) if f.endswith(TARBALL)]
        new_tarballs = False
        for tarball in tarballs:
            # m = re.match(TARBALL_MATCHER, tarball)
            # if m:
            #     print(m.group(1), m.group(2))
            if tarball not in self.cache['tarballs'] or force_new:
                self.cache['tarballs'][tarball] = {
                    'name': '',
                    'version': '',
                    'json': '',
                    'st_mtime': 0,
                    'mtime': '',
                    'ctime': ''
                }
                new_tarballs = True
        if force_new:
            self.cache['packages'] = {}
        if new_tarballs or force_new:
            self._write_cache()
        return new_tarballs or force_new

    def _construct_registry_entry(self, package_name):
        pass
        # versions_list.sort(key=lambda s: list(map(int, s.split('.'))))
        # versions_list.sort(key=lambda s: [int(u) for u in s.split('.')])
        # versions.sort(key=StrictVersion)

    def _extract_package_json(self, tarball, server_address):
        '''Extracts and stores information about the tarball.'''

        tarball_path = os.path.join(self.cache_dir, tarball)

        # Fill in times
        tarball_stat = os.stat(tarball_path)
        self.cache['tarballs'][tarball]['st_mtime'] = tarball_stat.st_mtime
        self.cache['tarballs'][tarball]['mtime'] = datetime.datetime.fromtimestamp(
            tarball_stat.st_mtime, tz=datetime.timezone.utc).isoformat()
        self.cache['tarballs'][tarball]['ctime'] = datetime.datetime.fromtimestamp(
            tarball_stat.st_ctime, tz=datetime.timezone.utc).isoformat()

        # Extract package.json
        tf = tarfile.open(tarball_path)
        package_json = tf.extractfile('package/package.json')
        package_json_str = ''.join([line.decode() for line in package_json])
        package_json_dict = json.loads(package_json_str)
        tf.close()

        name = package_json_dict.get('name')
        version = package_json_dict.get('version')
        author = package_json_dict.get('author', '')
        if isinstance(author, dict):
            print('AUTHOR IS DICT')

        if '_from' not in package_json_dict:
            package_json_dict['_from'] = '.'
        else:
            print('EXISTS: _from')

        if '_id' not in package_json_dict:
            package_json_dict['_id'] = '{}@{}'.format(name, version)
        else:
            print('EXISTS: _id')

        if '_nodeVersion' not in package_json_dict:
            package_json_dict['_nodeVersion'] = '5.7.1'
        else:
            print('EXISTS: _nodeVersion')

        if '_npmOperationalInternal' not in package_json_dict:
            package_json_dict['_npmOperationalInternal'] = {}
        else:
            print('EXISTS: _npmOperationalInternal')

        if '_npmUser' not in package_json_dict:
            package_json_dict['_npmUser'] = {'name': author}
        else:
            print('EXISTS: _npmUser')

        if '_npmVersion' not in package_json_dict:
            package_json_dict['_npmVersion'] = '3.6.0'
        else:
            print('EXISTS: _npmVersion')

        # Calculate SHA1 sum for tarball
        if '_shasum' not in package_json_dict:
            sha1 = hashlib.sha1()
            with open(tarball_path, 'rb') as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    sha1.update(data)
            package_json_dict['_shasum'] = sha1.hexdigest()
        else:
            print('EXISTS: _shasum')

        if 'directories' not in package_json_dict:
            package_json_dict['directories'] = {}
        else:
            print('EXISTS: directories')

        if 'dist' not in package_json_dict:
            package_json_dict['dist'] = {
                'shasum': sha1.hexdigest(),
                'tarball': '{}/{}'.format(server_address, tarball)
            }
        else:
            print('EXISTS: dist')

        if 'gitHead' not in package_json_dict:
            package_json_dict['gitHead'] = ''
        else:
            print('EXISTS: gitHead')

        if 'maintainers' not in package_json_dict:
            package_json_dict['maintainers'] = [{
                'name': author
            }]
        else:
            print('EXISTS: maintainers')

        if 'scripts' not in package_json_dict:
            package_json_dict['scripts'] = {}
        else:
            print('EXISTS: scripts')

        self.cache['tarballs'][tarball]['json'] = package_json_dict

        # Update name and version
        self.cache['tarballs'][tarball]['name'] = name
        self.cache['tarballs'][tarball]['version'] = version

        # TODO: Should be a set
        if name in self.cache['packages']:
            if tarball not in self.cache['packages'][name]:
                self.cache['packages'][name].append(tarball)
        else:
            self.cache['packages'][name] = [tarball]

    def get_package_json(self, package_name, server_address):
        need_update = False

        # Iterate through all tarballs that might match
        for key, value in self.cache['tarballs'].items():
            if value['name'] == package_name:
                # Definite match
                print('\t\tExisting tarball', key)
            elif key.startswith(package_name) and value['name'] == '':
                # Possible match
                print('\t\tPossible tarball', key)
                self._extract_package_json(key, server_address)
                need_update = True

        if need_update:
            self._write_cache()

        # Return a boolean indicating whether the package exists
        return (package_name in self.cache['packages'])


def main():
    pj = get_package_json('.', 'cli')
    print(pj)

if __name__ == '__main__':
    main()
