import tarfile
import json
import os
import re
import uuid
import hashlib
import datetime
from distutils.version import LooseVersion

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



# def generate_package_json_from_tarball(cache_dir, package_name, tarball_name, server_address):
#     tarball_path = os.path.join(cache_dir, tarball_name)
#     tarball_stat = os.stat(tarball_path)
#     tarball_mtime = datetime.datetime.fromtimestamp(tarball_stat.st_mtime, tz=datetime.timezone.utc).isoformat()
#     tarball_ctime = datetime.datetime.fromtimestamp(tarball_stat.st_ctime, tz=datetime.timezone.utc).isoformat()
#     tf = tarfile.open(tarball_path)
#     package_json = tf.extractfile('package/package.json')
#     package_json_str = ''.join([line.decode() for line in package_json])
#     package_dict = json.loads(package_json_str)
#     tf.close()
#
#     if package_dict['name'] == package_name:
#         print('Name matches package_name')
#
#         version = package_dict.get('version', '')
#
#         # Calculate SHA1 sum for tarball
#         sha1 = hashlib.sha1()
#         with open(tarball_path, 'rb') as f:
#             while True:
#                 data = f.read(65536)
#                 if not data:
#                     break
#                 sha1.update(data)
#
#         author = package_dict.get('author', '')
#         if isinstance(author, str) and author != '':
#             print('AUTHOR IS STRING', author)
#             m = re.match('(.*)<(.*)>', author)
#             if m:
#                 author_name = m.group(1).strip()
#                 author_email = m.group(2).strip()
#             else:
#                 author_name = author
#                 author_email = ''
#         elif isinstance(author, dict):
#             print('AUTHOR IS DICT')
#             author_name = author['name']
#             author_email = author['email']
#         else:
#             print('EMPTY AUTHOR ', type(author))
#             author_name = ''
#             author_email = ''
#
#         description = {}
#
#         description['_attachments'] = {}  # TODO:
#         description['_id'] = package_name
#         description['_rev'] = '1-{}'.format(uuid.uuid4().hex)  # TODO: Increment number?
#
#         description['author'] = {
#             'name': author_name,
#             'email': author_email
#         }
#
#         description['bugs'] = package_dict.get('bugs', '')
#         description['description'] = package_dict.get('description', '')
#
#         description['dist-tags'] = {}
#         description['dist-tags']['latest'] = version
#
#         description['homepage'] = package_dict.get('homepage', '')
#         description['keywords'] = package_dict.get('keywords', '')
#         description['license'] = package_dict.get('license', '')
#
#         description['maintainers'] = [{
#             'name': author_name,
#             'email': author_email
#         }]
#
#         description['name'] = package_name
#         description['readmeFilename'] = ''  # TODO:
#         description['repository'] = package_dict.get('repository', '')
#
#         description['time'] = {
#             'modified': tarball_mtime,
#             'created': tarball_ctime,
#             'version': tarball_mtime
#         }
#
#         description['versions'] = {}
#         description['versions'][version] = package_dict
#         # TODO
#         description['versions'][version]['_from'] = '.'
#         description['versions'][version]['_id'] = '{}@{}'.format(package_name, version)
#         description['versions'][version]['_nodeVersion'] = '5.7.1'
#         description['versions'][version]['_npmOperationalInternal'] = {}
#         description['versions'][version]['_npmUser'] = {
#             'email': author_email,
#             'name': author_name
#         }
#         description['versions'][version]['_npmVersion'] = '3.6.0'
#         description['versions'][version]['_shasum'] = sha1.hexdigest()
#         description['versions'][version]['directories'] = {}
#         description['versions'][version]['dist'] = {
#             'shasum': sha1.hexdigest(),
#             'tarball': '{}/{}'.format(server_address, tarball_name)
#         }
#         description['versions'][version]['gitHead'] = ''
#         description['versions'][version]['maintainers'] = [{
#             'email': author_email,
#             'name': author_name
#         }]
#         description['versions'][version]['scripts'] = {}
#
#         # TODO: Do we need these?
#         description['users'] = {}  # TODO:
#         description['readme'] = ''  # TODO:
#         description['contributors'] = package_dict.get('contributors', '')
#
#         # Now write the json file.
#         if os.path.exists(os.path.join(cache_dir, package_name)):
#             print('OVERWRITING')
#             with open(os.path.join(cache_dir, package_name), 'w') as f:
#                 f.write(json.dumps(description, sort_keys=True, indent=4))
#         else:
#             print('CREATING')
#             with open(os.path.join(cache_dir, package_name), 'w') as f:
#                 f.write(json.dumps(description, sort_keys=True, indent=4))
#         return True
#     else:
#         return False


# def get_package_json(cache_dir, package_name, server_address):
#     found = False
#     for entry in os.listdir(cache_dir):
#         if entry.startswith(package_name):
#             print('Found matching file:', entry)
#             if entry == package_name:
#                 # We've found our json file
#                 print('\tIs matching JSON file.')
#                 found = True
#                 break  # No need to go any further
#             elif entry.endswith(TARBALL):
#                 # We've found a package tarball that might fit
#                 print('\tIs matching tarball')
#                 found = generate_package_json_from_tarball(
#                     cache_dir=cache_dir,
#                     package_name=package_name,
#                     tarball_name=entry,
#                     server_address=server_address)
#
#     if found:
#         return package_name
#     else:
#         return None

TARBALL_MATCHER = re.compile('(.*)-([0-9].*).tgz')


class TarballCacher(object):
    def __init__(self, cache_dir, server_address, force_new=False):
        self.cache_dir = cache_dir
        self.server_address = server_address
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
        # print('_write_cache')
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4, sort_keys=True)

    def _update_cache(self, force_new=False):
        # print('_update_cache')
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
        versions = [self.cache['tarballs'][t] for t in self.cache['packages'].get(package_name, [])]
        versions.sort(key=lambda t: LooseVersion(t['version']))
        # print('Latest Version:', versions[-1]['version'])
        latest = versions[-1]
        # print(latest)
        registry = {
            '_attachments': latest['json'].get('_attachments', {}),  # TODO: Is this correct?
            '_id': package_name,
            '_rev': '1-{}'.format(uuid.uuid4().hex),  # TODO: Increment number?
            'author': latest['json'].get('author', ''),  # TODO: Should this be a dict?
            'bugs': latest['json'].get('bugs', ''),
            'description': latest['json'].get('description', ''),
            'dist-tags': {'latest': latest['version']},
            'homepage': latest['json'].get('homepage', ''),
            'keywords': latest['json'].get('keywords', ''),
            'license': latest['json'].get('license', ''),
            'maintainers': latest['json'].get('maintainers', []),  # TODO:
            'name': package_name,
            'readmeFilename': latest['json'].get('readmeFilename', ''),
            'repository': latest['json'].get('repository', ''),
            'time': {},
            'versions': {}
        }
        for version in versions:
            registry['time'][version['version']] = version['mtime']
            registry['versions'][version['version']] = version['json']
        registry['time']['created'] = latest['ctime']  # TODO: Should be earliest time
        registry['time']['modified'] = latest['mtime']
        return json.dumps(registry, sort_keys=True, indent=4)

    def _extract_package_json(self, tarball):
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
        try:
            # Usually here
            package_json = tf.extractfile('package/package.json')
        except KeyError as e:
            for n in tf.getnames():
                print(n)
                if 'package.json' in n:
                    package_json = tf.extractfile(n)
        package_json_str = ''.join([line.decode() for line in package_json])
        package_json_dict = json.loads(package_json_str)
        tf.close()

        name = package_json_dict.get('name')
        version = package_json_dict.get('version')
        author = package_json_dict.get('author', '')

        if '_from' not in package_json_dict:
            package_json_dict['_from'] = '.'
        else:
            print('\tEXISTS: _from')

        if '_id' not in package_json_dict:
            package_json_dict['_id'] = '{}@{}'.format(name, version)
        else:
            print('\tEXISTS: _id')

        if '_nodeVersion' not in package_json_dict:
            package_json_dict['_nodeVersion'] = '5.7.1'
        else:
            print('\tEXISTS: _nodeVersion')

        if '_npmOperationalInternal' not in package_json_dict:
            package_json_dict['_npmOperationalInternal'] = {}
        else:
            print('\tEXISTS: _npmOperationalInternal')

        if '_npmUser' not in package_json_dict:
            if isinstance(author, dict):
                # print('AUTHOR IS DICT')
                package_json_dict['_npmUser'] = author
            else:
                package_json_dict['_npmUser'] = {'name': author}
        else:
            print('\tEXISTS: _npmUser')

        if '_npmVersion' not in package_json_dict:
            package_json_dict['_npmVersion'] = '3.6.0'
        else:
            print('\tEXISTS: _npmVersion')

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
            print('\tEXISTS: _shasum')

        if 'directories' not in package_json_dict:
            package_json_dict['directories'] = {}
        # else:
        #     print('\tEXISTS: directories')

        if 'dist' not in package_json_dict:
            package_json_dict['dist'] = {
                'shasum': sha1.hexdigest(),
                'tarball': '{}/{}'.format(self.server_address, tarball)
            }
        else:
            print('\tEXISTS: dist')

        if 'gitHead' not in package_json_dict:
            package_json_dict['gitHead'] = ''
        else:
            print('\tEXISTS: gitHead')

        if 'maintainers' not in package_json_dict:
            package_json_dict['maintainers'] = [{
                'name': author
            }]
        # else:
        #     print('\tEXISTS: maintainers')

        if 'scripts' not in package_json_dict:
            package_json_dict['scripts'] = {}
        # else:
        #     print('\tEXISTS: scripts')

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

    @property
    def package_cache(self):
        return self.cache['packages']

    def get_package_json(self, package_name):
        need_update = False

        # Re-scan directory to see if any new tarballs added
        self._update_cache()

        # Iterate through all tarballs that might match
        for key, value in self.cache['tarballs'].items():
            if value['name'] == package_name:
                # Definite match
                # print('\tExisting tarball', key)
                if self.server_address not in value['json']['dist']['tarball']:
                    print('\tChanged server address for', key)
                    value['json']['dist']['tarball'] = '{}/{}'.format(self.server_address, key)
                    need_update = True
            elif key.startswith(package_name) and value['name'] == '':
                # Possible match
                print('\tPossible tarball', key)
                self._extract_package_json(key)
                need_update = True

        if need_update:
            self._write_cache()

        # Return a registry entry, or False
        if package_name in self.cache['packages']:
            return self._construct_registry_entry(package_name)
        else:
            return False


def main():
    pj = get_package_json('.', 'cli')
    print(pj)

if __name__ == '__main__':
    main()
