import optparse
parser = optparse.OptionParser()
parser.add_option('--in_FN', default=None, help='Input mol2 file')
parser.add_option('--out_FN', default=None, help='Output mol2 file')
parser.add_option('--net_charge', default=0, help='Net charge')
(args, options) = parser.parse_args()

import os
if not os.path.exists(args.in_FN):
  raise Exception(args.in_FN+' does not exist!')

print( 'Processing '+args.in_FN)

import chimera
ligand = chimera.openModels.open(args.in_FN)

try:
  chimera.runCommand("addcharge nonstd #0 %s method am1"%args.net_charge)
except:
  print( 'ANTECHAMBER failed, using Gasteiger charges')
  ligand[0].name = ligand[0].name + '-Gasteiger'
  chimera.runCommand("addcharge nonstd #0 %s method gas"%args.net_charge)

chimera.runCommand("write format mol2 0 {0}".format(args.out_FN))
