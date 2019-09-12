import networkx as nx
import sys

G=nx.read_edgelist(sys.argv[1],delimiter=';',nodetype=str)
with open(sys.argv[2],'w') as f:
  for cyc in nx.cycle_basis(G):
    for manifest in cyc:
      f.write(manifest+" ")
    f.write('\n')

