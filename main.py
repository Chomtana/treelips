import os
import config

#print(config.dropPercentage([]))

class ImageParts:
  pass

class PartTreeNode:
  def __init__(self, path, parent = None):
    self.path = path
    self.result = []
    self.children = []
    self.parent = parent

    self.distanceToLeaft = 0

    if parent is not None:
      parent.children.append(self)
  
  def addChildren(self, name):
    return PartTreeNode(self.path + [name], self)

  def getChildren(self, name):
    for child in self.children:
      if child.path[-1] == name:
        return child

  def isLeaf(self):
    return len(self.children) == 0

  # Print tree in DFS manner
  def print(self, level=0):
    print('-' * level, self.path, self.distanceToLeaft)
    for child in self.children:
      child.print(level + 1)

  def cacheDistanceToLeaf(self):
    dist = 0
    for child in self.children:
      dist = max(dist, child.cacheDistanceToLeaf() + 1)
    self.distanceToLeaft = dist
    return dist

  def dropPercentage(self):
    return config.dropPercentage(self)
  
  def layerOrder(self):
    return config.layerOrder(self)

  def partKey(self):
    return config.partKey(self)

  def partName(self):
    return config.partName(self)

  def isMerge(self):
    return config.isMerge(self)

partTreeRoot = PartTreeNode([])

def getPartTreeNode(path):
  if len(path) == 0: return partTreeRoot
  parent = getPartTreeNode(path[:-1])
  return parent.getChildren(path[-1])

def addPartTreeNode(path):
  node = getPartTreeNode(path[:-1])
  return node.addChildren(path[-1])

def buildPartsTree():
  layersLen = len('./layers')
  for root, subdirs, files in os.walk('./layers'):
    path = root[layersLen+1:].replace('\\', '/').split('/')
    files = list(filter(lambda file: file[0] != '.', files))

    if path[-1] == '': continue
    
    # print(path)
    # print(files)

    addPartTreeNode(path)

    for file in files:
      addPartTreeNode(path + [file])

  partTreeRoot.cacheDistanceToLeaf()

buildPartsTree()

partTreeRoot.print()