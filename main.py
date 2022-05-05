import os
import config
import random
from PIL import Image

BUILD_DIR = "./build"

#print(config.dropPercentage([]))

supplyCounter = 0

class ImageParts:
  def __init__(self, parts = []):
    self.parts = parts
    self.completed = False

  def addPart(self, part):
    self.parts.append(part)

  def setCompleted(self, completed):
    self.completed = completed

  @staticmethod
  def merge(partss):
    merged = []
    for parts in partss:
      merged.extend(parts.parts)
    return ImageParts(merged)

  def print(self):
    for node in self.parts:
      print(node.path)

  def buildImage(self):
    global supplyCounter

    layers = [(part.path, part.layerOrder(self.parts)) for part in self.parts]
    layers.sort(key = lambda x: x[1])

    images = [Image.open('./layers/' + '/'.join(layer[0])) for layer in layers]

    max_width = max(image.size[0] for image in images)
    max_height = max(image.size[1] for image in images)

    image_sheet = Image.new("RGBA", (max_width, max_height))

    for (i, image) in enumerate(images):
      image_sheet.paste(image, (
        max_width * 0 + (max_width - image.size[0]) // 2,
        max_height * 0 + (max_height - image.size[1]) // 2
      ), image.convert('RGBA'))

    if not os.path.exists(BUILD_DIR + "/images"):
      os.makedirs(BUILD_DIR + "/images")

    supplyCounter += 1
    image_sheet.save(BUILD_DIR + "/images/" + str(supplyCounter) + ".png")

EMPTY_PARTS = ImageParts()

class PartTreeNode:
  def __init__(self, path, parent = None):
    self.path = path
    self.result = []
    self.children = []
    self.parent = parent

    self.distanceToLeaf = 0

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

  def buildImageParts(self):
    if len(self.children) == 0:
      parts = ImageParts([self])
      return parts

    isMerge = self.isMerge()
    childParts = []
    dropRate = []

    for child in self.children:
      parts = child.buildImageParts()
      childParts.append(parts)
      dropRate.append(child.dropPercentage(parts))

    if isMerge:
      return ImageParts.merge(childParts)
    else:
      return random.choices(population=childParts, weights=dropRate)[0]

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

  def resetSelectedCount(self):
    self.selectedCount = 0
    for child in self.children:
      child.resetSelectedCount()

  def dropPercentage(self, parts = EMPTY_PARTS):
    return config.dropPercentage(self, parts)
  
  def layerOrder(self, parts = EMPTY_PARTS):
    return config.layerOrder(self, parts)

  def partKey(self, parts = EMPTY_PARTS):
    return config.partKey(self, parts)

  def partName(self, parts = EMPTY_PARTS):
    return config.partName(self, parts)

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
print("============================")
partTreeRoot.buildImageParts().buildImage()