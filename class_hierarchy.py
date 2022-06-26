import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

def get_subclasses(cls,l=0):
    subs = cls.__subclasses__()
    if subs:
        res = [(l,cls.__name__, sub.__name__) for sub in subs]
        for sub in subs:
                res.extend(get_subclasses(sub,l+1))
    else:
        res = [(l,cls.__name__,None)]
    return res

    
def get_subclasses_graph(Ts):
    g = nx.DiGraph()
    for color, (T, starting_level) in enumerate(Ts):
        res = (
            pd.DataFrame(
                get_subclasses(T, starting_level), 
                columns=['source_layer','source','target'])
            .assign(color=color)
        )
        res[['source','target']] = (
            res[['source','target']]
            .apply(
                lambda s: 
                s
                .str.replace('(?<=\w)_','\n…_', regex=True)
                .str.replace('(?<=[a-z])(?=[A-Z])','\n…', regex=True)
                )
        )


        for layer_name, layer in res.groupby('source_layer'):
            g.add_nodes_from(layer[['source', 'target']].stack().dropna().values, layer=layer_name,color=color)
        for layer_name, layer in res.groupby('source_layer'):    
            g.add_edges_from(list(layer[['source', 'target']].dropna().to_records(index=False)))

    return g



def plot_subclasses_graph(Ts, size=16, node_size=1e4):
    g = get_subclasses_graph(Ts)
    colors = [node[1]['color'] for node in g.nodes.data()]
    plt.figure(figsize=(size,size))
    ax = plt.axes()
    nx.draw_networkx(
        g, 
        pos=nx.multipartite_layout(
            g, 
            subset_key='layer',
            align='horizontal'
        ), 
        with_labels=True, 
        alpha=0.9, 
        arrows=True, 
        ax=ax,
        node_size=node_size,
        font_size=12,
        node_color=colors,
        node_shape='h'
    )