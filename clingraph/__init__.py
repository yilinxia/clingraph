from clingo.application import Application, clingo_main, Flag
from clingo.symbol import Function
from graphviz import Graph, Digraph

class Clingraph(Application):
    program_name = 'clingraph'
    version = '0.1.0-dev'

    option_group = 'Clingraph Options'

    render = Flag(False)
    view = Flag(False)

    directory = 'out'
    format = None
    engine = None

    type = 'type'
    node = 'node'
    edge = 'edge'
    attr = 'attr'

    def main(self, ctl, files):
        for path in files:
            ctl.load(path)
        if not files:
            ctl.load('-')
        ctl.ground([('base', [])], context=self)
        ctl.solve()

    def register_options(self, options):
        options.add_flag(
            self.option_group,
            'render',
            'Render the answers',
            self.render,
        )

        options.add_flag(
            self.option_group,
            'view',
            'Render the answers and show them with the default viewer',
            self.view
        )

        def parse(value):
            self.directory = value
            return True
        options.add(
            self.option_group,
            'directory',
            'Directory for source saving and rendering',
            parse,
            argument='<path>'
        )

        def parse(value):
            self.format = value
            return True
        options.add(
            self.option_group,
            'format',
            'Rendering output format',
            parse,
            argument='<format>'
        )

        def parse(value):
            self.engine = value
            return True
        options.add(
            self.option_group,
            'engine',
            'Layout command used',
            parse,
            argument='<engine>'
        )

        def parse(value):
            self.type = value
            return True
        options.add(
            self.option_group,
            'type',
            'Predicate that defines whether the graph is directed or undirected',
            parse,
            argument='<name>'
        )

        def parse(value):
            self.node = value
            return True
        options.add(
            self.option_group,
            'node',
            'Predicate that defines nodes',
            parse,
            argument='<name>'
        )

        def parse(value):
            self.edge = value
            return True
        options.add(
            self.option_group,
            'edge',
            'Predicate that defines edges',
            parse,
            argument='<name>'
        )

        def parse(value):
            self.attr = value
            return True
        options.add(
            self.option_group,
            'attr',
            'Predicate that defines attributes',
            parse,
            argument='<name>'
        )

    def print_model(self, model, printer):
        types = []
        nodes = []
        edges = []
        attrs = {}

        for atom in model.symbols(shown=True):
            if atom.match(self.type, 1):
                types.append(str(atom.arguments[0]))

            elif any((atom.match(self.node, arity) for arity in [1, 2])):
                nodes.append(tuple(map(str, atom.arguments)))

            elif any((atom.match(self.edge, arity) for arity in [2, 3])):
                edges.append(tuple(map(str, atom.arguments)))

            elif atom.match(self.attr, 3):
                key = atom.arguments[0]

                if key.match('', 2):
                    key = tuple(map(str, atom.arguments[0].arguments))
                else:
                    key = str(atom.arguments[0])

                attrs[key] = { str(atom.arguments[1]): str(atom.arguments[2]) }

        if types in [[], ['graph']]:
            _Graph = Graph
        elif types in [['digraph']]:
            _Graph = Digraph
        else:
            pass # TODO: Report an error.

        graph = _Graph(
            name = f'{model.number:04d}',
            directory = self.directory,
            format = self.format,
            engine = self.engine,
        )

        for node in nodes:
            graph.node(*node, _attributes=attrs.get(node[0]))

        for edge in edges:
            graph.edge(*edge, _attributes=attrs.get(edge[0:2]))

        if self.render or self.view:
            path = graph.render(
                view=self.view,
                cleanup=True,
                quiet_view=self.view,
            )
            print(f'Saved to {path}')
        else:
            print(graph.source)

def main():
    clingo_main(Clingraph())
