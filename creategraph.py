#!/usr/bin/env python3
from dataclasses import dataclass
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

BOX = Namespace("http://fitlayout.github.io/ontology/render.owl#")
SEGM = Namespace("http://fitlayout.github.io/ontology/segmentation.owl#")
R = Namespace("http://fitlayout.github.io/resource/")

@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float

@dataclass
class Tag:
    uri: str
    support: float

SIMPLE_VALUES = {
    "backgroundColor": BOX.backgroundColor,
    "color": BOX.color,
    "contentLength": BOX.contentLength,
    "documentOrder": BOX.documentOrder,
    "fontFamily": BOX.fontFamily,
    "fontSize": BOX.fontSize,
    "fontStyle": BOX.fontStyle,
    "fontWeight": BOX.fontWeight,
    "lineThrough": BOX.lineThrough,
    "underline": BOX.underline,
    "text": SEGM.text
}

def extractChunkData(g, chunkSubject):
    data = {}
    for key, value in SIMPLE_VALUES.items():
        data[key] = g.value(chunkSubject, value)
    data["bounds"] = extractChunkBounds(g, chunkSubject)
    data["tags"] = extractChunkTags(g, chunkSubject)
    return data

def extractChunkBounds(g, chunkSubject):
    bounds = g.value(chunkSubject, BOX.bounds)
    if bounds is not None:
        x = g.value(bounds, BOX.positionX)
        y = g.value(bounds, BOX.positionY)
        width = g.value(bounds, BOX.width)
        height = g.value(bounds, BOX.height)
        return Rect(x, y, width, height)
    else:
        return None

def extractChunkTags(g, chunkSubject):
    tags = []
    tagSubjects = g.objects(chunkSubject, SEGM.tagSupport)
    for tagSubject in tagSubjects:
        tagUri = g.value(tagSubject, SEGM.hasTag)
        support = g.value(tagSubject, SEGM.support)
        tags.append(Tag(tagUri, support))
    return tags

def extractChunks(g):
    chunks = []
    chunkSubjects = g.subjects(RDF.type, SEGM.TextChunk);
    for chunkSubject in chunkSubjects:
        data = extractChunkData(g, chunkSubject)
        chunks.append(data)
    return chunks

def hasTag(chunk, tagUri):
    for tag in chunk["tags"]:
        if tag.uri == tagUri:
            return True
    return False

g = Graph()
g.parse("art9.ttl", format="turtle")

chunks = extractChunks(g)
selectedTagUri = R["tag-generic--title"]
for chunk in chunks:
    if selectedTagUri is None or hasTag(chunk, selectedTagUri):
        print(chunk["text"], chunk["bounds"].x, chunk["fontSize"], chunk["tags"])
