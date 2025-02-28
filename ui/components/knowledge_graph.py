import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random
import pandas as pd
from typing import List, Dict, Any, Optional

def knowledge_graph(
    nodes: List[Dict[str, Any]], 
    edges: List[Dict[str, Any]], 
    title: str = "Knowledge Graph", 
    height: int = 600,
    node_size_field: Optional[str] = None,
    node_color_field: Optional[str] = None,
    edge_width_field: Optional[str] = None,
    edge_color_field: Optional[str] = None,
    node_hover_data: Optional[List[str]] = None,
    edge_hover_data: Optional[List[str]] = None
):
    """
    Create an interactive knowledge graph visualization.
    
    Args:
        nodes: List of node dictionaries with at least 'id' and 'label' fields
        edges: List of edge dictionaries with at least 'source', 'target', and 'label' fields
        title: Title of the graph
        height: Height of the visualization in pixels
        node_size_field: Optional field name to use for node size
        node_color_field: Optional field name to use for node color
        edge_width_field: Optional field name to use for edge width
        edge_color_field: Optional field name to use for edge color
        node_hover_data: Optional list of field names to show on node hover
        edge_hover_data: Optional list of field names to show on edge hover
    """
    # Create a network graph
    G = nx.Graph()
    
    # Add nodes
    for node in nodes:
        node_id = node['id']
        G.add_node(node_id)
        for key, value in node.items():
            G.nodes[node_id][key] = value
    
    # Add edges
    for edge in edges:
        source = edge['source']
        target = edge['target']
        G.add_edge(source, target)
        for key, value in edge.items():
            G[source][target][key] = value
    
    # Use a spring layout for node positions
    # This can be replaced with other layout algorithms
    pos = nx.spring_layout(G, seed=42)
    
    # Extract node positions
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    
    # Configure node appearance
    if node_size_field and node_size_field in G.nodes[list(G.nodes())[0]]:
        node_sizes = [G.nodes[node][node_size_field] * 10 if G.nodes[node][node_size_field] else 10 for node in G.nodes()]
    else:
        node_sizes = [10] * len(G.nodes())
    
    if node_color_field and node_color_field in G.nodes[list(G.nodes())[0]]:
        node_colors = [G.nodes[node][node_color_field] for node in G.nodes()]
    else:
        node_colors = ['#1f77b4'] * len(G.nodes())
    
    # Create hover text for nodes
    node_hover_text = []
    for node in G.nodes():
        hover_text = f"ID: {node}<br>"
        if 'label' in G.nodes[node]:
            hover_text += f"Label: {G.nodes[node]['label']}<br>"
        
        if node_hover_data:
            for field in node_hover_data:
                if field in G.nodes[node]:
                    hover_text += f"{field}: {G.nodes[node][field]}<br>"
        
        node_hover_text.append(hover_text)
    
    # Extract edge positions
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Configure edge appearance
    if edge_width_field:
        edge_widths = []
        for u, v in G.edges():
            width = G[u][v].get(edge_width_field, 1)
            edge_widths.extend([width, width, None])
    else:
        edge_widths = [1] * len(edge_x)
    
    if edge_color_field:
        edge_colors = []
        for u, v in G.edges():
            color = G[u][v].get(edge_color_field, '#888')
            edge_colors.extend([color, color, None])
    else:
        edge_colors = ['#888'] * len(edge_x)
    
    # Create hover text for edges
    edge_hover_text = []
    for u, v in G.edges():
        hover_text = f"Source: {G.nodes[u].get('label', u)}<br>Target: {G.nodes[v].get('label', v)}<br>"
        
        if 'label' in G[u][v]:
            hover_text += f"Relationship: {G[u][v]['label']}<br>"
        
        if edge_hover_data:
            for field in edge_hover_data:
                if field in G[u][v]:
                    hover_text += f"{field}: {G[u][v][field]}<br>"
        
        edge_hover_text.extend([hover_text, hover_text, None])
    
    # Create edges trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        mode='lines',
        line_width=edge_widths,
        line_color=edge_colors,
        text=edge_hover_text
    )
    
    # Create nodes trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=node_sizes,
            color=node_colors,
            line_width=2
        ),
        text=node_hover_text
    )
    
    # Create the figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=height
        )
    )
    
    # Display the figure
    st.plotly_chart(fig, use_container_width=True)

def taxonomy_tree_visualization(
    taxonomy_tree: List[Dict[str, Any]], 
    title: str = "Taxonomy Tree",
    height: int = 600
):
    """
    Create an interactive tree visualization for taxonomy hierarchy.
    
    Args:
        taxonomy_tree: List of taxonomy nodes in tree structure format
        title: Title of the visualization
        height: Height of the visualization in pixels
    """
    # Extract nodes and edges from the taxonomy tree
    nodes = []
    edges = []
    
    def process_node(node, parent_id=None):
        node_id = node['id']
        nodes.append({
            'id': node_id,
            'label': node['name'],
            'description': node.get('description', ''),
            'level': node.get('level', 0)
        })
        
        if parent_id is not None:
            edges.append({
                'source': parent_id,
                'target': node_id,
                'label': 'parent_of'
            })
        
        for child in node.get('children', []):
            process_node(child, node_id)
    
    # Process all root nodes
    for root_node in taxonomy_tree:
        process_node(root_node)
    
    # Call the general knowledge graph function
    knowledge_graph(
        nodes=nodes,
        edges=edges,
        title=title,
        height=height,
        node_size_field='level',
        node_hover_data=['description', 'level']
    )

def concept_relationships_visualization(
    concepts: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]], 
    title: str = "Concept Relationships",
    height: int = 600
):
    """
    Create an interactive visualization for game design concept relationships.
    
    Args:
        concepts: List of game design concepts
        relationships: List of relationships between concepts
        title: Title of the visualization
        height: Height of the visualization in pixels
    """
    # Convert concepts to nodes
    nodes = []
    for concept in concepts:
        nodes.append({
            'id': concept['id'],
            'label': concept['name'],
            'description': concept.get('description', ''),
            'is_verified': concept.get('is_verified', False),
            'confidence': concept.get('confidence_score', 1.0)
        })
    
    # Convert relationships to edges
    edges = []
    for rel in relationships:
        edges.append({
            'source': rel['source_id'],
            'target': rel['target_id'],
            'label': rel.get('relationship_type', 'related'),
            'strength': rel.get('strength', 1.0)
        })
    
    # Call the general knowledge graph function
    knowledge_graph(
        nodes=nodes,
        edges=edges,
        title=title,
        height=height,
        node_color_field='confidence',
        edge_width_field='strength',
        node_hover_data=['description', 'is_verified'],
        edge_hover_data=['strength']
    ) 