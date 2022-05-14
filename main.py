import os
import config
import random
import json
import threading
import sys
from copy import deepcopy
from PIL import Image

BUILD_DIR = "./build"
FOLDER_TEMPLATE = config.folderTemplate()

METADATA_NAME = config.name()
METADATA_DESCRIPTION = config.description()

supplyOffset = config.supplyOffset()
totalSupply = config.totalSupply()

def buildFolderName(variants):
  result = []
  for key in FOLDER_TEMPLATE:
    if key in variants:
      result.append(variants[key])
  return '/'.join(result)

class ImageParts:
  def __init__(self, parts = []):
    self.parts = parts
    self.completed = False
    self.tokenId = 0

  def addPart(self, part):
    self.parts.append(part)

  def setCompleted(self, completed):
    self.completed = completed

  @staticmethod
  def merge(selection):
    merged = []
    variants = dict()
    for parts in selection:
      merged.extend(parts[0].parts)
      for key in parts[1]:
        if key and key in variants and variants[key] != parts[1][key]:
          print(variants)
          print(key)
          print(parts[1])
          print(selection)
          raise Exception("Cannot merge different variant and same key")
        variants[key] = parts[1][key]
    return (ImageParts(merged), variants)

  def print(self):
    for node in self.parts:
      print(node.path)

  def buildImage(self):
    tokenId = self.tokenId

    layers = [(part.path, part.layerOrder(self.parts)) for part in self.parts]
    layers.sort(key = lambda x: x[1])

    images = [Image.open('./layers/' + '/'.join(layer[0])) for layer in layers]

    max_width = max(image.size[0] for image in images)
    max_height = max(image.size[1] for image in images)

    image_sheet = Image.new("RGBA", (max_width, max_height))

    for (i, image) in enumerate(images):
      image_sheet = Image.alpha_composite(image_sheet, image)

    variants = dict()
    attributes = dict()

    for part in self.parts:
      nodeToRoot = part.nodeToRoot()

      for node in nodeToRoot:
        key = node.partVariantKey()
        partName = node.partName()
        if not key: continue
        if key in variants and variants[key] != partName:
          print(key, partName, variants[key])
          raise Exception("Variant conflict")
        else:
          variants[key] = partName

      for node in nodeToRoot:
        key = node.partKey()
        partName = node.partName()
        if not key: continue
        if key in attributes and attributes[key] != partName:
          print(key, partName, attributes[key])
          raise Exception("Attributes conflict")
        else:
          attributes[key] = partName

    print(variants)

    jsonData = dict()

    # To be compiled layer once checked
    if METADATA_NAME:
      jsonData['name'] = METADATA_NAME
    
    if METADATA_DESCRIPTION:
      jsonData['description'] = METADATA_DESCRIPTION

    jsonData['image'] = 'ipfs://{imageHash}/{tokenId}.png'
    jsonData['attributes'] = []

    for key in attributes:
      jsonData['attributes'].append({
        "trait_type": key,
        "value": attributes[key]
      })

    outputDir = BUILD_DIR + "/images/" + buildFolderName(variants)
    outputJsonDir = BUILD_DIR + "/json/" + buildFolderName(variants)
    outputPartDir = BUILD_DIR + "/parts/" + buildFolderName(variants)

    if not os.path.exists(outputDir):
      os.makedirs(outputDir)

    if not os.path.exists(outputJsonDir):
      os.makedirs(outputJsonDir)

    if not os.path.exists(outputPartDir):
      os.makedirs(outputPartDir)

    image_sheet.save(outputDir + "/" + str(tokenId) + ".png")

    with open(outputJsonDir + "/" + str(tokenId) + ".json", "w", encoding="utf-8") as f:
      json.dump(jsonData, f, indent=4)

    with open(outputPartDir + "/" + str(tokenId) + ".json", "w", encoding="utf-8") as f:
      partsJson = []
      for node in self.parts:
        partsJson.append(node.path)
      json.dump(partsJson, f, indent=4)

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

  def buildImageParts(self, variantsRequired = None):
    if variantsRequired is None: variantsRequired = dict()

    #print(self.path, variantsRequired)
    
    if len(self.children) == 0:
      parts = ImageParts([self])
      variantKey = self.partVariantKey()
      variants = dict()
      if variantKey:
        variants[variantKey] = self.partName()
      return (parts, variants)

    isMerge = self.isMerge()
    childParts = []
    childSelection = []

    for child in self.children:
      (parts, variants) = child.buildImageParts(deepcopy(variantsRequired))

      if parts is None: continue

      # Merge variants
      if isMerge:
        for key in variants:
          if key and key in variantsRequired and variantsRequired[key] != variants[key]:
            print(variantsRequired)
            print(key)
            print(variants)
            raise Exception("Cannot merge sibling with different variant and same key")
          variantsRequired[key] = variants[key]

      childParts.append(parts)
      childSelection.append((parts, variants, child.dropPercentage(parts)))

    if isMerge:
      (parts, variants) = ImageParts.merge(childSelection)

      variantKey = self.partVariantKey(childParts)
      if variantKey:
        variants[variantKey] = self.partName(childParts)

      return (parts, variants)
    else:
      #print('VARIANT', variantsRequired)
      #print(*childSelection, sep='\n')
      #print('BEFORE', childSelection)

      for variantKey in variantsRequired:
        childSelection = list(filter(lambda x: variantKey not in x[1] or x[1][variantKey] == variantsRequired[variantKey], childSelection))

      if len(childSelection) == 0:
        #print('EMPTY', self.partVariantKey(childParts), self.partName(childParts), self.path)
        return (None, None)

      #print('AFTER', childSelection)

      dropRate = list(map(lambda x: x[2], childSelection))
      (parts, variants, dropRateSingle) = random.choices(population=childSelection, weights=dropRate)[0]

      variantKey = self.partVariantKey(childParts)
      if variantKey:
        variants[variantKey] = self.partName(childParts)

      #print('***')

      return (parts, variants)

  def nodeToRoot(self):
    node = self
    result = []
    while node.parent is not None:
      result.append(node)
      node = node.parent
    return result

  # Print tree in DFS manner
  def print(self, level=0):
    print('-' * level, self.path, self.isMerge())
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

  def partVariantKey(self, parts = EMPTY_PARTS):
    return config.partVariantKey(self, parts)

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

imagesParts = []

def buildThread():
  while len(imagesParts) > 0:
    parts = imagesParts[-1]
    imagesParts.pop()
    parts.print()
    parts.buildImage()
    print("============================")

partTreeRoot.print()
print("============================")

if False:
  imagesParts = [None] * totalSupply

  for root, subdirs, files in os.walk('./build/parts'):
    for f in files:
      if not f.endswith('.json'): continue
      parts = json.load(open(root + '/' + f, encoding='utf-8'))
      tokenId = int(f.split('.')[0])
      imagesParts[tokenId - 1] = ImageParts(list(map(lambda x: getPartTreeNode(x), parts)))
      imagesParts[tokenId - 1].tokenId = tokenId
else:
  for i in range(totalSupply):
    parts = partTreeRoot.buildImageParts()
    parts[0].tokenId = i + supplyOffset
    imagesParts.append(parts[0])

imagesParts = imagesParts[::-1]

for i in range(config.threadCount()):
  thread = threading.Thread(target=buildThread)
  thread.start()