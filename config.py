import re

def folderTemplate():
  return ["Gang", "rarity", "Type", "set"]

def name():
  return ""

def description():
  return ""

def threadCount():
  return 5

def supplyOffset():
  return 1

def totalSupply():
  return 1000

# Can exceed 1, to be normalized later, used for selection mode
def dropPercentage(node, parts):
  path = node.path
  if len(path) == 0: return 1

  if '$' in path[-1]:
    return extractNumberFromDelimiter(path[-1], '$')

  if node.isLeaf():
    return 1
  else:
    return 0

# Order of layer, only called from leaf
def layerOrder(node, parts):
  path = node.path
  if len(path) == 0: return []

  orders = []
  for name in path:
    if '#' in name:
      orders.append(extractNumberFromDelimiter(name, '#'))
  return orders

def partVariantKey(node, parts):
  path = node.path
  if len(path) == 0: return None

  if node.isLeaf():
    result = None
    for name in path:
      if '@' in name:
        partKeyLevel = getKeyLevel(name)
        if partKeyLevel == 3:
          result = cleanName(name)
    return result

  pathParts = path[-1].split('@')
  if len(pathParts) < 2: return None
  return pathParts[-1]

def partKey(node, parts):
  path = node.path

  if len(path) == 0: return None

  if node.isLeaf():
    result = None
    for name in path:
      if '@' in name:
        partKeyLevel = getKeyLevel(name)
        if partKeyLevel == 3:
          result = cleanName(name)
    return result

  partKeyLevel = getKeyLevel(path[-1])

  if partKeyLevel != 1: return None
  
  pathParts = path[-1].split('@')
  if len(pathParts) < 2: return None
  return pathParts[-1]

def partName(node, parts):
  path = node.path
  if len(path) == 0: return ""
  return cleanName(path[-1])

# If it is merge path, we will merge all children in result instead of selecting one
def isMerge(node):
  if node.isLeaf(): return False

  allHasRate = True
  for child in node.children:
    if '$' not in child.path[-1] and not child.isLeaf():
      allHasRate = False

  return not allHasRate

def extractNumberFromDelimiter(s, delimiter):
  parts = s.split(delimiter)
  if len(parts) <= 1: return None
  return int(re.findall(r"(\d+)(?=\D|$)", parts[-1])[0])

def getKeyLevel(s):
  # if '@@@@@@' in s: return 6
  # elif '@@@@@' in s: return 5
  # elif '@@@@' in s: return 4
  if '@@@' in s: return 3
  elif '@@' in s: return 2
  elif '@' in s: return 1
  return 0

def cleanName(name):
  name = re.findall('^(.*?)[$@#.]', name)[0]
  for i in range(len(name)):
    if not name[i].isdigit():
      name = name[i:]
      break
  return name
