import re

def description():
  return "Just for test"

def totalSupply():
  return 100

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

def partKey(node, parts):
  path = node.path
  if len(path < 2): return ""
  return path[-2]

def partName(node, parts):
  path = node.path
  if len(path == 0): return ""
  return path[-1]

# If it is merge path, we will merge all children in result instead of selecting one
def isMerge(node):
  if node.isLeaf(): return True

  allHasRate = True
  for child in node.children:
    if '$' not in child.path[-1]:
      allHasRate = False

  return not allHasRate

def extractNumberFromDelimiter(s, delimiter):
  parts = s.split(delimiter)
  if len(parts) <= 1: return None
  return int(re.findall(r"(\d+)(?=\D|$)", parts[-1])[0])
