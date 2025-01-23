# modules/visualization.py
from graphviz import Digraph
from typing import List

def plot_causal_chain(causes: List[str], output_path: str):
    dot = Digraph(comment='EASA Causal Chain')
    for i, cause in enumerate(causes):
        dot.node(f'C{i}', cause)
        if i > 0: 
            dot.edge(f'C{i-1}', f'C{i}')
    dot.render(output_path)