from flask import g

from py2neo import authenticate, Graph


def connect_db():
    authenticate("localhost:7474", "neo4j", "0000")
    return Graph()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'graph_db'):
        g.graph_db = connect_db()
        return g.graph_db


def get_actor(actor_id):
    graph = get_db()
    if isinstance(actor_id, int):
        try:
            actor_id = str(int)
        except ValueError:
            raise Exception
    node = graph.find_one('Actor', 'id', actor_id)
    if not node:
        raise Exception

    ctx = {}
    properties = node.get_properties()
    films = []
    if properties:
        for film in graph.match(start_node=node, rel_type='ACTS_IN'):
            film_props = film.end_node.get_properties()
            films.append(
                {'title': film_props['title'],
                 'film_id': film_props['id']}
            )

        ctx.update(
            {
                'name': properties['name'],
                'bio': properties['biography'],
                'films': films,
            }
        )

    return ctx
