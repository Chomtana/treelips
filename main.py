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
  
  def addChildren(self, node):
    self.children.append(node)

  def dropPercentage(self):
    return config.dropPercentage(self.path)

partTreeRoot = PartTreeNode([])

def getPartTreeNode(path):
  

def addPartTreeNode(path):


def buildPartsTree():
  layersLen = len('./layers')
  for root, subdirs, files in os.walk('./layers'):
    path = root[layersLen+1:].replace('\\', '/').split('/')
    files = list(filter(lambda file: file[0] != '.', files))
    print(path)
    print(files)

buildPartsTree()