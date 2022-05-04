# Can exceed 1, to be normalized later, used for selection mode
def dropPercentage(node):
  return 1

# Order of layer, only called from leaf
def layerOrder(node):
  key = partKey(node)
  return 1

def partKey(node):
  path = node.path
  if len(path < 2): return ""
  return path[-2]

def partName(node):
  path = node.path
  if len(path == 0): return ""
  return path[-1]

# If it is merge path, we will merge all children in result instead of selecting one
def isMerge(node):
  if node.isLeaf(): return True
  if node.distanceToLeaf == 1: return False
  return True