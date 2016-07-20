# localnpmjs
Offline registry.npmjs.org emulator.

## Why?

Not all web development is connected to the internet.

I have an air-gapped system on which I develop code for internal use. I want access
to the nodejs/npm ecosystem, but npm assumes access to registry.npmjs.org.

Unlike pip, the python installer, I cannot just point to a local directory and say
'install everything from here'. The official response for 'offline' npm is to
replicate their couchdb database - a ridiculous proposition.

Sinopia is a caching registry solution, but it requires npm to install it - leaving
me with a chicken and egg problem.

## What?

A webserver written in Python 3, that serves the registry information and the tarballs
for true offline npm use.

## How?

Run the script:

    python3 npmjs.py --port=8000 --cache=/path/to/cache/directory

Set your npm registry:

    npm config set registry "http://localhost:8000"

Install your desired packages:

    npm install <package_name>

## Caveats

  - Currently only supports single package versions.
  - It's crude
  - No https
