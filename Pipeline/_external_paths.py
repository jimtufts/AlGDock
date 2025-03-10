# _external_paths in Pipeline directory
import os, inspect
dir_external_paths = os.path.dirname(os.path.abspath(\
  inspect.getfile(inspect.currentframe())))

### Google drive downloader from
# http://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive
import requests

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
###

def findPath(locations):
  """
  Parses a list of locations, returning the first file that exists.
  If none exist, then None is returned.
  """
  import os.path
  for location in locations:
    if location is not None and os.path.exists(location):
      return os.path.abspath(location)
  return None

def findPaths(keys):
  """
  Finds a path for each key.
  """
  paths = {}
  for key in keys:
    paths[key] = findPath(search_paths[key]) \
      if key in search_paths.keys() else None
    if paths[key] is None:
      # Download file and install program if available
      if key in download_paths.keys():
        (FN,command,path) = download_paths[key]
        # Check that it has not already been downloaded
        import os
        if os.path.isfile(path):
          paths[key] = os.path.abspath(path)
        else:
          import time
          download_start_time = time.time()
          print( 'Downloading and installing '+key)
          os.system('wget --no-verbose --no-check-certificate ' + \
            'http://stash.osgconnect.net/+daveminh/%s'%(FN))
          if not os.path.isfile(FN):
            download_file_from_google_drive(google_drive_hash[FN], FN)
          os.system('tar xzf %s'%FN)
          if command != '':
            os.system(command)
          if os.path.isfile(path):
            print( '  ' + key + ' downloaded and installed in %f s'%(\
              time.time() - download_start_time))
            paths[key] = os.path.abspath(path)
          else:
            print( 'Could not download '+key)
            raise Exception('Could not download '+key)
      else:
        raise Exception('Missing file for '+key)
  return paths

# Define search paths for external programs and files
# Defined for
# David's IIT MacBook Pro, WH210, and the CCB cluster
search_paths = {
# These files/programs are used in the pipeline
     'balloon':['/Users/dminh/Installers/Balloon-1.5.0.1143/balloon',
                '/Applications/Darwin_64bit-Balloon/balloon',
                '/share/apps/balloon/1.5.0.1143/balloon'],
               # For adding hydrogens and charges to receptors
     'pdb2pqr':['/Users/dminh/Applications/pdb2pqr-osx-bin-1.9.0/pdb2pqr',
                '/share/apps/pdb2pqr/1.9.0/pdb2pqr'],
               # For adding hydrogens and charges to ligands
     'chimera':['/Applications/Chimera.app/Contents/MacOS/chimera', # same in WH210
                '/share/apps/chimera/1.11/bin/chimera'],
               # For initial ligand pose
       'dock6':['/Users/dminh/Installers/dock6/bin/dock6',
                '/Applications/dock6/dock6',
                '/share/apps/dock/6/bin/dock6',
                '/home/dminh/software/dock6/bin/dock6',
                '/home/daveminh/software/dock6/bin/dock6',
                '/g/g19/minh1/software/dock6/bin/dock6'],
               # Submits a command to the queue
'qsub_command':['/Users/dminh/scripts/qsub_command.py',
                '~/scripts/qsub_command.py',
                '/home/dminh/scripts/qsub_command.py',
                '/home/daveminh/scripts/qsub_command.py',
                '/g/g19/minh1/scripts/qsub_command.py'],
               # Spheres for UCSF DOCK 6
  'sphgen_cpp':['/Users/dminh/Applications/sphgen_cpp.1.2/sphgen_cpp',
                '/Applications/dock6/sphgen',
                '/share/apps/sphgen_cpp/1.2/sphgen_cpp'],
               # Preparing the system for AMBER
      'sander':['/Users/dminh/Installers/amber16/bin/sander',
                '/Applications/amber16/bin/sander',
                '/share/apps/amber/16/bin/sander'],
               # Calculating a Poisson-Boltzmann Grid
        'apbs':['/Users/dminh/Applications/APBS-1.4.1/APBS.app/Contents/MacOS/apbs',
                '/share/apps/apbs/1.4/bin/apbs'],
               # Generalized AMBER force field
        'gaff':['/Users/dminh/Installers/AlGDock-0.0.1/Data/gaff2.dat',
                '/home/dminh/Installers/AlGDock-0.0.1/Data/gaff2.dat',
                '/home/daveminh/algdock_data/gaff2.dat'],
               # AlGDock
     'algdock':['/Users/dminh/Library/Enthought/Canopy_64bit/User/lib/python2.7/site-packages/AlGDock/BindingPMF.py',
                '/share/apps/canopy/1.5.0/Canopy_64bit/User/lib/python2.7/site-packages/AlGDock/BindingPMF.py']}

algdock_setup = '''
# Modify paths
echo "
search_paths = {
  'gaff2.dat':[None],
  'catdcd':[None],
  'namd':[None],
  'sander':[None],
  'MMTK':['$WORK_DIR/AlGDock/MMTK'],
  'vmd':['$WORK_DIR/vmd/bin/vmd']}
" | cat AlGDock/AlGDock/_external_paths.py - > paths.py
mv paths.py AlGDock/AlGDock/_external_paths.py
export ALGDOCK=$WORK_DIR/AlGDock/BindingPMF
'''

# The file to download, special installation commands, and the final location
download_paths = {
  'balloon':('balloon.tar.gz','','Balloon-1.5.0.1143/balloon'),
  'chimera':('chimera.tar.gz', \
    './chimera-1.9-linux_x86_64.bin < chimera_install.in', \
    'chimera-1.9/bin/chimera'),
  'dock6':('dock6.tar.gz','','dock6/bin/dock6'),
  'apbs':('APBS-1.4-linux-static-x86_64.tar.gz','','APBS-1.4-linux-static-x86_64/bin/apbs'),
  'algdock':('algdock.tar.gz',algdock_setup,'AlGDock/BindingPMF')}

google_drive_hash = {
  'namd.tar.gz':'0ByidOA_rkLLSSXZzbURFbWdxNkU', \
  'sander.tar.gz':'0ByidOA_rkLLSejFDMnh4TFlFNFU', \
  'elsize.tar.gz':'0ByidOA_rkLLSb0tHZ0w2SFJPSmc', \
  'gbnsr6.tar.gz':'0ByidOA_rkLLSLWpGb0FUd1J4dms', \
  'ambpdb.tar.gz':'0ByidOA_rkLLSNklqdFp6cU9rWVE', \
  'molsurf.tar.gz':'0ByidOA_rkLLSeVhMdlRHN1RqdHc', \
  'APBS-1.4-linux-static-x86_64.tar.gz':'0ByidOA_rkLLSa3BYcmpOZlNONGM',
  'balloon.tar.gz':'0ByidOA_rkLLSQjItRzVUQXVXYmc', \
  'chimera.tar.gz':'0ByidOA_rkLLSbE1oNUFmZll6VEU', \
  'dock6.tar.gz':'0ByidOA_rkLLScXE0a0w2MXptOGc', \
  'algdock.tar.gz':'0ByidOA_rkLLSV29xTUtWcUVIVnM'
}
