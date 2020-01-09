import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import pandas as pd
import os
import numpy as np
import sys
import matplotlib.pyplot as plt
from collections import OrderedDict, defaultdict

def get_color_type(node_type):
    if node_type in 'FUNCTION':
        return 'orange'
    elif node_type in 'BASICBLOCK':
        return 'blue'
    elif node_type in 'INSTRUCTION':
        return 'green'
    else:
        return 'gray'
data_path="/home/sip/eval"
output_path=data_path
if(len(sys.argv)>1):
  data_path = sys.argv[1]
  output_path = sys.argv[2]
print("data_path:{} output_path:{}".format(data_path,output_path))
data_dir = os.path.expanduser(data_path)
edgelist = pd.DataFrame()
column_names=['uid','name','type']
node_data = pd.read_csv(os.path.join(data_dir, "vertices.csv"),lineterminator='\n', sep=';', header=None,index_col=False,dtype={'uid':object}, names=column_names)
node_data.set_index('uid', inplace=True)
print('Finished reading nodes!')
print(node_data)
edges = pd.read_csv(os.path.join(data_dir, "rel.csv"),index_col=False, sep=';', header=None, names=["source", "target"],dtype={'source': object, 'target':object})

print(edges)
g = nx.from_pandas_edgelist(edges,create_using=nx.MultiDiGraph)
nx.set_node_attributes(g, node_data.name.to_dict(), 'id')
nx.set_node_attributes(g, node_data.type.to_dict(), 'type')
#inst_nodes = node_data[node_data['type']=='INSTRUCTION']
#print(inst_nodes)
#for index, _ in inst_nodes.iterrows():
#  g.remove_node(index)
node_inst=nx.get_node_attributes(g,'type')
for k in node_inst:
  if node_inst[k] in 'INSTRUCTION':
    g.remove_node(k)

pos = nx.nx_pydot.graphviz_layout(g)

plt.figure(num=None, figsize=(10, 10), dpi=80)
plt.axis('off')
print(g.nodes())
node_colors= {k:get_color_type(v) for k,v in node_inst.items()}
print(node_colors)
nx.draw(g,pos,node_color=node_colors,with_labels = True)
#nx.draw_spring(g,with_labels = True)
ColorLegend = {'Function': 'orange','BasicBlock': 'blue','Instruction': 'green','Other': 'gray'}
ax = plt.gca()
for label in ColorLegend:
  ax.plot([0],[0],color=ColorLegend[label],label=label)

pos_attrs = {}
for node, coords in pos.items():
    pos_attrs[node] = (coords[0], coords[1] + 0.08)
node_attrs=nx.get_node_attributes(g,'id')
#node_attrs = {int(k):v for k,v in node_attrs.items()}
#custom_node_attrs = {}
#for node, attr in node_attrs.items():
#    custom_node_attrs[node] = "{'type': '" + attr + "'}"

#print (node_attrs)
nx.draw_networkx_labels(g, pos_attrs, labels=node_attrs)
plt.legend()
plt.show()


cut = 1.00
xmax = cut * max(xx for xx, yy in pos.values())
ymax = cut * max(yy for xx, yy in pos.values())
plt.xlim(0, xmax)
plt.ylim(0, ymax)

plt.savefig("Graph.png", format="PNG",bbox_inches="tight")
#pr=nx.pagerank(g, alpha=0.9)
#print(pr)
