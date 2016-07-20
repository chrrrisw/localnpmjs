import tarfile
import json
import os
import re
import uuid
import hashlib


def generate_package_json_from_tarball(cache_dir, package_name, tarball_name):
    tf = tarfile.open(os.path.join(cache_dir, tarball_name))
    package_json = tf.extractfile('package/package.json')
    package_json_str = ''.join([line.decode() for line in package_json])
    package_dict = json.loads(package_json_str)
    tf.close()

    if package_dict['name'] == package_name:
        print('Name matches package_name')

        version = package_dict.get('version', '')

        sha1 = hashlib.sha1()
        with open(os.path.join(cache_dir, tarball_name), 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        author = package_dict.get('author', '')
        if isinstance(author, str) and author != '':
            print('AUTHOR IS STRING')
            m = re.match('(.*)<(.*)>', author)
            author_name = m.group(1).strip()
            author_email = m.group(2).strip()
        elif isinstance(author, dict):
            print('AUTHOR IS DICT')
            author_name = author['name']
            author_email = author['email']
        else:
            print('EMPTY AUTHOR ', type(author))
            author_name = ''
            author_email = ''

        description = {}

        description['_id'] = package_name
        description['_rev'] = '1-{}'.format(uuid.uuid4().hex)  # TODO: Increment number?
        description['name'] = package_name
        description['description'] = package_dict.get('description', '')

        description['dist-tags'] = {}
        description['dist-tags']['latest'] = version

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
            'tarball': ''
        }
        description['versions'][version]['gitHead'] = ''
        description['versions'][version]['maintainers'] = [{
            'email': author_email,
            'name': author_name
        }]
        description['versions'][version]['scripts'] = {}

        description['maintainers'] = [{
            'name': author_name,
            'email': author_email
        }]

        description['time'] = {
            'modified': '',  # TODO:
            'created': '',  # TODO:
            version: ''  # TODO:
        }

        description['author'] = {
            'name': author_name,
            'email': author_email
        }

        description['repository'] = package_dict.get('repository', '')

        description['users'] = {}  # TODO:

        description['readme'] = ''  # TODO:

        description['homepage'] = package_dict.get('homepage', '')

        description['keywords'] = package_dict.get('keywords', '')

        description['contributors'] = package_dict.get('contributors', '')

        description['bugs'] = package_dict.get('bugs', '')

        description['readmeFilename'] = ''  # TODO:

        description['license'] = package_dict.get('license', '')

        description['_attachments'] = {}  # TODO:

        # print(json.dumps(description, sort_keys=True, indent=4))
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


def get_package_json(cache_dir, package_name):
    found = False
    for entry in os.listdir(cache_dir):
        if entry.startswith(package_name):
            print('Found matching file:', entry)
            if entry == package_name:
                # We've found our json file
                print('\tIs matching JSON file.')
                found = True
                break  # No need to go any further
            elif entry.endswith('tgz'):
                # We've found a package tarball that might fit
                print('\tIs matching tarball')
                found = generate_package_json_from_tarball(
                    cache_dir=cache_dir,
                    package_name=package_name,
                    tarball_name=entry)

    if found:
        return package_name
    else:
        return None


def main():
    pj = get_package_json('.', 'cli')
    print(pj)

if __name__ == '__main__':
    main()
