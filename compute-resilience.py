import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import pandas as pd
import os
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib import colors
from collections import OrderedDict, defaultdict
import math
from centrality import *
from functools import partial
from itertools import chain
from more_itertools import unique_everseen
import json
ColorLegend = {'Basic Block & Instruction': 'green','BasicBlock': 'blue', 'Instruction':'orange', 'Other':'gray'}
def get_unique_protection_edges(G,nbunch=None, distance=None):
    if G.is_directed():
        G = G.reverse()
    spl = partial(nx.shortest_path, G)
    return {u: chain.from_iterable(d for d in spl(source=u).values()) for u in G.nbunch_iter(nbunch)} 
def get_scores(protection):
  localizability={'sc':0.8,'oh':0.4,'cfi':0.5}
  defeatability={'sc':'A','oh':'A','cfi':'A'}
  return (localizability[protection],defeatability[protection])
def print_scores(header,scores):
  print('*******{}*******'.format(header))
  scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
  for n, c in scores.items():
    print(n, c)
def get_color(k,instcoverages,blockcoverages):
    instcoverage=0
    blockcoverage=0
    if k in instcoverages:
        instcoverage=instcoverages[k]
    if k in blockcoverages:
        blockcoverage=blockcoverages[k]
    if blockcoverage and instcoverage >0:
        return 'green'
    elif blockcoverage>0:
        return 'blue'
    elif instcoverage>0:
        return 'orange'
    else:
        return 'gray'
def load_graph(node_data,edges):
  g = nx.from_pandas_edgelist(edges,create_using=nx.DiGraph)
  #calculate pagerank
  pr=nx.pagerank(g, alpha=1)
  harmonic, sumEdges, longestChain = harmonic_centrality(g)
  nx.set_node_attributes(g, node_data.instcoverage.to_dict(), 'instcoverage')
  nx.set_node_attributes(g, node_data.bbcoverage.to_dict(), 'bbcoverage')
  nx.set_node_attributes(g, node_data.name.to_dict(), 'type')
  nx.set_node_attributes(g, node_data.hostingfunction.to_dict(), 'hostingfunction')
  nx.set_node_attributes(g, pr, 'pagerank')
  nx.set_node_attributes(g, harmonic, 'centrality')
  nx.set_node_attributes(g, longestChain, 'longestchain')
  nx.set_node_attributes(g, sumEdges, 'sumedges')
  return g
def read_csv(data_path):
  print("data_path:{} ".format(data_path))
  data_dir = os.path.expanduser(data_path)
  edgelist = pd.DataFrame()
  column_names=['uid','name','hostingfunction','instcoverage','bbcoverage']
  node_data = pd.read_csv(os.path.join(data_dir, "manifests.csv"),lineterminator='\n', sep=';', header=None,index_col=False,dtype={'uid':object}, names=column_names)
  node_data.set_index('uid', inplace=True)
  print('Finished reading nodes!')
  edges = pd.read_csv(os.path.join(data_dir, "manifestsrel.csv"),index_col=False, sep=';', header=None, names=["source", "target"],dtype={'source': object, 'target':object})
  print('Finished reading edges')
  return node_data,edges
def main(argv):
  data_path="/home/sip/eval"
  output_path=data_path
  if(len(sys.argv)!=3):
      print("Usage: compute_resilience.py data_path output_path")
      exit(1)
  data_path = sys.argv[1]
  output_path = sys.argv[2]
  node_data,edges=read_csv(data_path)
  g = load_graph(node_data, edges)
  #print(set(node_data.index.values))
  #print(set(g.nodes))
  #manifests not protected by others do not appear on the graph
  norel_manifests=set(node_data.index.values).difference(set(g.nodes))
  #print(node_data)
  #print(norel_manifests)
  #for m in norel_manifests:
  #  print(m)
  missing_manifests=node_data.loc[norel_manifests]
  dump_defeatability(g,missing_manifests,output_path)
  dump_graph(g,output_path)


def dump_defeatability(g,missing_manifests,output_path):
  node_attrs=nx.get_node_attributes(g,'type')
  hostingfunction_attrs=nx.get_node_attributes(g,'hostingfunction')
  distinct_edges=get_unique_protection_edges(g)
  nodeResilience = {}
  functionResilience = {}
  for node, protectors in distinct_edges.items():
    nodeResilience[node]=list(unique_everseen(protectors))
    nodeFunction = hostingfunction_attrs[node]
    if nodeFunction not in functionResilience:
      functionResilience[nodeFunction]=[]
    #print(node,node_attrs[node],hostingfunction_attrs[node],list(unique_everseen(protectors)))
    #print(node,list(unique_everseen(protectors)), functionResilience[nodeFunction])
    node_protectors = unique_everseen(chain(nodeResilience[node],functionResilience[nodeFunction])) 
    #SC nodes residing in the function should not be counted as function protectors
    #CFI and OH guards on the other hand must be counted as function protectors
    functionProtectors = []
    for nprotect in node_protectors:
      #print(hostingfunction_attrs[nprotect], nodeFunction, node_attrs[nprotect])
      if hostingfunction_attrs[nprotect] == nodeFunction and node_attrs[nprotect] in 'sc':
        continue
      functionProtectors.append(nprotect)
    #print(node_protectors)
    functionResilience[nodeFunction]=functionProtectors
  functionDefeatability=[]
  for f,uniqueNodes in functionResilience.items():
    #print(f,uniqueNodes)
    countMissingManifests=missing_manifests.loc[missing_manifests['hostingfunction']==f].size
    functionDefeatability.append(len(uniqueNodes)+countMissingManifests)
  print('mean:',np.mean(functionDefeatability))
  mean=np.mean(functionDefeatability)
  print('median:',np.median(functionDefeatability))
  median=np.median(functionDefeatability)
  print('std:',np.std(functionDefeatability))
  std=np.std(functionDefeatability)
  result={}
  result['functions']=functionResilience
  result['mean']=mean
  result['median']=median
  result['std']=std
  with open(os.path.join(output_path,'defeatability.json'),'w') as f:
    json.dump(result,f)


def estimate_defeatability(data_path,output_path):
  node_data,edges=read_csv(data_path)
  g=load_graph(node_data,edges)
  dump_defeatability(g,output_path)

def dump_graph(g,output_path):
  pos = nx.nx_pydot.graphviz_layout(g)
  plt.figure(num=None, figsize=(20, 20), dpi=70)
  plt.axis('off')
  #print(g.nodes())
  instcoverage = nx.get_node_attributes(g,'instcoverage')
  bbcoverage=nx.get_node_attributes(g,'bbcoverage')
  #print('inst coverage attr',instcoverage)
  #print('bb coverage attr',bbcoverage)
  node_colors= [get_color(k,instcoverage,bbcoverage) for k in g.nodes()]
  node_sizes= [round(v*40000,0)+300 for k,v in nx.get_node_attributes(g,'pagerank').items()]
  #print('node sizes:',node_sizes)
  #print('node colors:',node_colors)
  nx.draw(g,pos,node_size=node_sizes,node_color=node_colors,with_labels = True)
  #nx.draw_spring(g,with_labels = True)
  ax = plt.gca()
  for label in ColorLegend:
    ax.plot([0],[0],color=ColorLegend[label],label=label)

  pos_attrs = {}
  for node, coords in pos.items():
    pos_attrs[node] = (coords[0], coords[1] + 8.08)
  pagerank_attrs=nx.get_node_attributes(g,'pagerank')

  
  hostingfunction_attrs=nx.get_node_attributes(g,'hostingfunction')
  harmonic=nx.get_node_attributes(g,'centrality')
  longestChain=nx.get_node_attributes(g,'longestchain')
  node_attrs=nx.get_node_attributes(g,'type')
  node_attrs = {k:v for k,v in node_attrs.items()}
  custom_node_attrs = {}
  #print(node_attrs)
  #print(pagerank_attrs)
  for node, attr in node_attrs.items():
    custom_node_attrs[node] = "{}[{}](pr:{})(hc:{})(lc:{})".format(hostingfunction_attrs[node],attr,round(pagerank_attrs[node],2),round(harmonic[node],2),longestChain[node])

  #print (node_attrs)
  nx.draw_networkx_labels(g, pos_attrs, labels=custom_node_attrs)
  plt.legend()
  plt.show()


  cut = 1.3
  xmax = cut * max(xx for xx, yy in pos.values())
  ymax = cut * max(yy for xx, yy in pos.values())
  plt.xlim(0, xmax)
  plt.ylim(0, ymax)

  plt.savefig(os.path.join(output_path,"Graph.png"), format="PNG",bbox_inches="tight")





if __name__ == "__main__":
    main(sys.argv)



def dump_graph_metrics():
  ###############################GRAPH METRICS############################
  phi = (1 + math.sqrt(5)) / 2.0  # largest eigenvalue of adj matrix
  centrality = nx.katz_centrality(g, 1/phi - 0.01)
  print_scores('katz centrality',centrality)

  eigen_centrality=nx.eigenvector_centrality_numpy(g)
  print_scores('eigenvector_centrality', eigen_centrality)

  load_centrality=nx.load_centrality(g)
  print_scores('load_centrality',load_centrality)

  average_neighbor_degree=nx.average_neighbor_degree(g,source='out', target='out')
  print_scores('average_neighbor_degree',average_neighbor_degree)

  k_nearest_neighbors=nx.average_degree_connectivity(g,source='in',target='in')
  print_scores('k_nearest_neighbors',k_nearest_neighbors)

  closeness_centrality=nx.closeness_centrality(g)
  print_scores('closeness_centrality',closeness_centrality)

  degree_centrality=nx.degree_centrality(g)
  print_scores('degree_centrality',degree_centrality)


  betweenness_centrality=nx.betweenness_centrality(g)
  print_scores('betweenness_centrality',betweenness_centrality)
  hubs,authorities=nx.hits(g)
  print_scores('hubs',hubs)
  print_scores('auhtorities',authorities)


  from networkx.algorithms import approximation as approx
  node_connectivity=approx.node_connectivity(g)
  print('node_connectivity',node_connectivity)




#print(pr)
