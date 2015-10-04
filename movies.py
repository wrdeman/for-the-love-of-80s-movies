import igraph
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import linregress

from py2neo import authenticate
from py2neo import Graph as pGraph


class MovieGraph(igraph.Graph):
    def __init__(self):
        authenticate("localhost:7474", "neo4j", "0000")

    def build_graph(self, random=False):
        neo4j = pGraph()
        # actors - movies
        print "getting data from neo4j"

        query = """
        MATCH (p1:Actor)-[:ACTS_IN]->(m:Movie)
        RETURN p1.name, m.title
        """
        data = neo4j.cypher.execute(query)

        actors = list(set([datum[0] for datum in data]))
        movies = list(set([datum[1] for datum in data]))

        query = """
        MATCH (p1:Director)-[:DIRECTED]->(m:Movie)
        RETURN p1.name, m.title
        """
        data1 = neo4j.cypher.execute(query)

        directors = list(set([datum[0] for datum in data1]))
        movies1 = list(set([datum[1] for datum in data1]))

        print "building vertices"
        self.graph = igraph.Graph()
        self.graph.add_vertices(actors)
        self.graph.vs['actor'] = True
        self.graph.vs['movie'] = False
        self.graph.vs['director'] = False

        self.graph.add_vertices(list(set(movies+movies1)))
        for v in self.graph.vs:
            if not v['actor']:
                v['movie'] = True
                v['actor'] = False
                v['director'] = False

        for d in directors:
            try:
                v = self.graph.vs.find(name=d)
                v['director'] = True
            except:
                self.graph.add_vertex(
                    name=d,
                    **{
                        'movie': False,
                        'actor': False,
                        'director': True
                    }
                )
        print "connecting vertices"
        if random:
            # todo make random network connections
            pass
        else:
            for datum in data:
                self.graph.add_edge(
                    datum[0], datum[1], **{'label': 'acts_in'}
                )
                for datum in data1:
                    self.graph.add_edge(
                        datum[0], datum[1], **{'label': 'directs'}
                    )

    def is_actor(self, vertex):
        if vertex['actor']:
            return True
        return False

    def is_director(self, vertex):
        if vertex['director']:
            return True
        return False

    def is_movie(self, vertex):
        if vertex['movie']:
            return True
        return False

    def is_person(self, vertex):
        if vertex['actor'] or vertex['director']:
            return True
        return False

    def is_da(self, vertex):
        if vertex['actor'] and vertex['director']:
            return True
        return False

    def str_person(self, vertex):
        if vertex['actor'] and vertex['director']:
            return "%s (%s)" % (vertex['name'], 'da')
        elif vertex['actor']:
            return "%s (%s)" % (vertex['name'], 'a')
        elif vertex['director']:
            return "%s (%s)" % (vertex['name'], 'd')

    def print_centrality(
            self, name='degree', limit=10, person=True, movie=False
    ):
        """ print out the top top 10 of a measure of centrality

        name = igraph method e.g. degree, pagerank
        """
        def if_type():
            if person:
                return self.is_person(self.graph.vs[i])
            if movie:
                return self.is_movie(self.graph.vs[i])
            return True

        centrality = [
            (i, deg)
            for i, deg in enumerate(self.graph.__getattribute__(name)())
            if if_type()
        ]

        for v in sorted(centrality, key=lambda x: x[1], reverse=True)[0:limit]:
            print self.str_person(self.graph.vs[v[0]]), v[1]

    def print_neighbours(self, name):
        print name
        src = self.graph.vs(name_eq=name)
        for dst in list(set(self.graph.neighbors(name))):
            # get multiple edges
            edges = [
                edge
                for edge in self.graph.es[self.graph.incident(src['name'][0])]
                if edge.target == dst
            ]

            for edge in list(set(edges)):
                print edge['label'], self.graph.vs[dst]['name']

    def richclub(
            self,
            fraction=0.1,
            highest=True,
            scores=None,
            indices_only=False
    ):
        """Extracts the "rich club" of the given graph, i.e. the subgraph spanned
        between vertices having the top X% of some score.

        Scores are given by the vertex degrees by default.

        @param graph:    the graph to work on
        @param fraction: the fraction of vertices to extract; must be between 0 and 1.
        @param highest:  whether to extract the subgraph spanned by the highest or
                         lowest scores.
        @param scores:   the scores themselves. C{None} uses the vertex degrees.
        @param indices_only: whether to return the vertex indices only (and not the
                              subgraph)
        """

        if scores is None:
            scores = self.graph.degree()

        indices = range(self.graph.vcount())
        indices.sort(key=scores.__getitem__)

        n = int(round(self.vcount() * fraction))
        if highest:
            indices = indices[-n:]
        else:
            indices = indices[:n]

        if indices_only:
            return indices

        return self.graph.subgraph(indices)

    def hist(self, log=True, plot=True):
        """ plot a histgram of the degrees
        """
        bins = self.graph.degree_distribution().bins()
        xs, ys = zip(*[
            (left, count)
            for left, _, count in bins
            if count > 0 and left > 0
        ])

        slope, _, _, _, _ = linregress(
            np.log(np.array(xs)), np.log(np.array(ys))
        )
        print "Slope = %s" % slope

        if plot:
            plt.plot(np.log(xs), np.log(ys))
            plt.show()

    def global_efficiency(self):
        E = []
        N = len(self.graph.vs)
        for v in self.graph.vs:
            a = 1./np.array(self.graph.shortest_paths(source=v)[0])
            E_i = np.ma.masked_invalid(a).sum() / (N * (N - 1))
            E.append(E_i)

        E_total = sum(E)
        V = [(E_total - ee) / E_total for ee in E]
        return E_total, V
