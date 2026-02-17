from flclient import SEGM
from config import fl

#
# Deletes all tag assignments from the repository so that tags can be reassigned using the tagging.py script.
# It simply deletes all quads with the predicates "segm:hasTag" and "segm:tagSupport".
#
fl.delete_quad(None, SEGM["hasTag"], None)
fl.delete_quad(None, SEGM["tagSupport"], None)
