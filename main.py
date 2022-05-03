import os
import config

#print(config.dropPercentage([]))

class PartTreeNode:
  def __init__(self, path, parent = None):
    self.path = path
    self.result = []
    self.children = []
    self.parent = parent

    if parent is not None:
      parent.addChildren(self)
  
  def addChildren(self, name):
    return PartTreeNode(self.path + [name], self)

  def getChildren(self, name):
    for child in self.children:
      if child.path[-1] == name:
        return child

  def dropPercentage(self):
    return config.dropPercentage(self.path)

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
    print(path)
    print(files)

buildPartsTree()