import requests

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF


class FitLayoutClient:
    """ REST client for FitLayout """

    def __init__(self, api_root, repository_id):
        self.api_root = api_root
        self.repository_id = repository_id
    
    def repo_endpoint(self):
        return f"{self.api_root}/r/{self.repository_id}"
    
    def sparql(self, query):
        """ Executes a SPARQL query on the repository """
        url = f"{self.repo_endpoint()}/repository/query"
        headers = { "Content-Type": "application/sparql-query" }
        response = requests.post(url, data=query, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "results" in data and "bindings" in data["results"]:
            for binding in data["results"]["bindings"]:
                row = {}
                for key, value in binding.items():
                    row[key] = decode_json_value(value)
                yield row
        else:
            return []
        
    def artifacts(self, type = None):
        """ Returns a list of all artifacts in the repository """
        query = default_prefix_string()
        if (type is None):
            query += "SELECT ?pg WHERE { ?pg rdf:type ?type . ?type rdfs:subClassOf fl:Artifact }"
        else:
            query += " SELECT ?pg WHERE { ?pg rdf:type <" + str(type) + "> }\n"
        for row in self.sparql(query):
            yield row["pg"]
    
    def get_artifact(self, uri):
        """ Returns a single artifact from the repository """
        url = f"{self.repo_endpoint()}/artifact/item/" + requests.utils.quote(str(uri), safe="")
        headers = { "Accept": "text/turtle" }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.text
        g = Graph()
        g.parse(data=data, format="turtle")
        return g


def decode_json_value(value):
    """ Decodes a value from the FitLayout API into a Python object """
    if value["type"] == "uri":
        return URIRef(value["value"])
    elif value["type"] == "literal":
        return Literal(value["value"], datatype=value["datatype"])
    else:
        return value["value"]

def default_prefixes():
    return {
        "fl": "http://fitlayout.github.io/ontology/fitlayout.owl#",
        "r": "http://fitlayout.github.io/resource/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "box": "http://fitlayout.github.io/ontology/render.owl#",
        "segm": "http://fitlayout.github.io/ontology/segmentation.owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }

def default_prefix_string():
    prefixes = default_prefixes()
    return "\n".join(f"PREFIX {prefix}: <{value}>" for prefix, value in prefixes.items())

BOX = Namespace("http://fitlayout.github.io/ontology/render.owl#")
SEGM = Namespace("http://fitlayout.github.io/ontology/segmentation.owl#")
R = Namespace("http://fitlayout.github.io/resource/")
