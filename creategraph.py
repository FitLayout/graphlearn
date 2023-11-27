from dataclasses import dataclass
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, XSD

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

class GraphCreator:
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
        "text": SEGM.text,
    }

    def __init__(self):
        self.g = Graph()

    def load(self, file_path):
        self.g.parse(file_path, format="turtle")

    def extract_chunks(self):
        chunks = []
        chunk_subjects = self.g.subjects(RDF.type, SEGM.TextChunk)
        for chunk_subject in chunk_subjects:
            data = self.extract_chunk_data(chunk_subject)
            chunks.append(data)
        return chunks

    def extract_chunk_data(self, chunk_subject):
        data = {}
        for key, value in self.SIMPLE_VALUES.items():
            data[key] = self.g.value(chunk_subject, value)
        data["bounds"] = self.extract_chunk_bounds(chunk_subject)
        data["tags"] = self.extract_chunk_tags(chunk_subject)
        return data

    def extract_chunk_bounds(self, chunk_subject):
        bounds = self.g.value(chunk_subject, BOX.bounds)
        if bounds is not None:
            x = self.g.value(bounds, BOX.positionX)
            y = self.g.value(bounds, BOX.positionY)
            width = self.g.value(bounds, BOX.width)
            height = self.g.value(bounds, BOX.height)
            return Rect(x, y, width, height)
        else:
            return None

    def extract_chunk_tags(self, chunk_subject):
        tags = []
        tag_subjects = self.g.objects(chunk_subject, SEGM.tagSupport)
        for tag_subject in tag_subjects:
            tag_uri = self.g.value(tag_subject, SEGM.hasTag)
            support = self.g.value(tag_subject, SEGM.support)
            tags.append(Tag(tag_uri, support))
        return tags

    def has_tag(self, chunk, tag_uri):
        for tag in chunk["tags"]:
            if tag.uri == tag_uri:
                return True
        return False
    
    # A function that takes a list of tags and returns a list of their URIs
    def get_tag_uris(self, tags):
        tag_uris = []
        for tag in tags:
            tag_uris.append(tag.uri)
        return tag_uris


if __name__ == "__main__":
    print(XSD.int)
    gc = GraphCreator()
    gc.load("art9.ttl")
    chunks = gc.extract_chunks()
    selected_tag_uri = R["tag-generic--title"]
    for chunk in chunks:
        if selected_tag_uri is None or gc.has_tag(chunk, selected_tag_uri):
            print(
                chunk["text"],
                chunk["bounds"].x,
                chunk["fontSize"],
                gc.get_tag_uris(chunk["tags"]),
            )