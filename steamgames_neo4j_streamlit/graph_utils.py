import math
import networkx as nx
import plotly.graph_objects as go


def _records_to_graph(records, node_keys, rel_keys):
    """
    Convert Neo4j records to a NetworkX graph.
    We keep:
      - group: label (Game, Tag, Publisher, ...)
      - role:  variable name in the query (g, other, tag, ...)
    """
    G = nx.Graph()

    for rec in records:
        # Helper: access by key both for neo4j.Record and dict
        def get_val(key):
            if hasattr(rec, "__getitem__"):
                try:
                    return rec[key]
                except Exception:
                    pass
            if isinstance(rec, dict):
                return rec.get(key)
            return None

        # ---------- Nodes ----------
        for key in node_keys:
            node = get_val(key)
            if node is None:
                continue

            # neo4j.graph.Node
            if hasattr(node, "id"):
                node_id = node.id
                labels = list(getattr(node, "labels", []))
                group = labels[0] if labels else key
                props = dict(node)
            elif isinstance(node, dict):
                props = node
                base = props.get("name") or props.get("title") or key
                node_id = f"{key}:{base}"
                group = key
            else:
                continue

            # Create node if missing, then always update attributes
            if node_id not in G:
                G.add_node(node_id)

            G.nodes[node_id]["label"] = (
                props.get("name") or props.get("title") or group
            )
            G.nodes[node_id]["group"] = group
            G.nodes[node_id]["role"] = key  # g / other / tag / sourceGame / node / etc.



        # ---------- Relationships ----------
        for key in rel_keys:
            rel = get_val(key)
            if rel is None:
                continue

            if hasattr(rel, "start_node_id"):
                start_id = rel.start_node_id
                end_id = rel.end_node_id
                rel_type = rel.type
            elif hasattr(rel, "nodes"):
                start_id = rel.nodes[0].id
                end_id = rel.nodes[1].id
                rel_type = getattr(rel, "type", key)
            elif isinstance(rel, dict):
                start_id = rel.get("start_node_id") or rel.get("start")
                end_id = rel.get("end_node_id") or rel.get("end")
                rel_type = rel.get("type", key)
                if start_id is None or end_id is None:
                    continue
            else:
                continue

            G.add_edge(start_id, end_id, type=rel_type)

    return G


def _radial_layout_q7(G):
    """
    Custom layout:
      - center:     main game(s)
      - middle ring: tags
      - outer ring: other games / nodes
    """
    center_nodes = []
    tag_nodes = []
    other_nodes = []

    for n, attrs in G.nodes(data=True):
        role = attrs.get("role")
        group = attrs.get("group")

        # center for both Q7 ("g") and Q0 ("sourceGame")
        if role in ("g", "sourceGame"):
            center_nodes.append(n)
        elif role == "tag" or group == "Tag":
            tag_nodes.append(n)
        else:
            other_nodes.append(n)

    pos = {}

    # Center: main game(s)
    for n in center_nodes:
        pos[n] = (0.0, 0.0)

    def place_circle(nodes, radius):
        if not nodes:
            return
        step = 2 * math.pi / len(nodes)
        for i, n in enumerate(nodes):
            angle = i * step
            pos[n] = (radius * math.cos(angle), radius * math.sin(angle))

    # Tags in middle ring, similar/recommended games in outer ring
    place_circle(tag_nodes, radius=1.0)
    place_circle(other_nodes, radius=2.0)

    return pos


def build_network_figure(records, node_keys, rel_keys, title="Graph", layout_mode="spring"):
    """
    Build a Plotly figure (nodes + edges) from Neo4j records for Streamlit.

    layout_mode:
      - "spring"      -> force-directed layout (default)
      - "q7_radial"   -> concentric rings (main game, tags, similar games)
    """
    G = _records_to_graph(records, node_keys, rel_keys)

    if G.number_of_nodes() == 0:
        return None

    # ---------- Layout ----------
    if layout_mode == "q7_radial":
        pos = _radial_layout_q7(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    # ---------- Edges: highlight edges connected to the main game ----------
    primary_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("role") in ("g", "sourceGame")]

    primary_edge_x = []
    primary_edge_y = []
    other_edge_x = []
    other_edge_y = []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        if u in primary_nodes or v in primary_nodes:
            primary_edge_x += [x0, x1, None]
            primary_edge_y += [y0, y1, None]
        else:
            other_edge_x += [x0, x1, None]
            other_edge_y += [y0, y1, None]

    other_edge_trace = go.Scatter(
        x=other_edge_x,
        y=other_edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1, color="rgba(180,180,180,0.4)"),
        showlegend=False,
    )

    primary_edge_trace = go.Scatter(
        x=primary_edge_x,
        y=primary_edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1.5, color="rgba(255, 220, 120, 0.6)"),
        showlegend=False,
    )

    # ---------- Nodes: grouped traces so we get a legend ----------

    # base colors per node group (label)
    group_colors = {
        "Game": "#ffcc00",       # normal games
        "Publisher": "#ff7f0e",
        "Developer": "#1f77b4",
        "Genre": "#a9ebf5",
        "Tag": "#d62728",
        "Language": "#9467bd",
    }
    default_color = "#1f77b4"

    SOURCE_GAME_COLOR = "#48c66a" 

    # display_group -> {x, y, text, hover, size, color}
    grouped_nodes = {}

    for node_id, attrs in G.nodes(data=True):
        x, y = pos[node_id]
        group = attrs.get("group", "Other")
        label = attrs.get("label", str(node_id))
        role = attrs.get("role")

        # Decide color & size
        if role in ("sourceGame", "g"):
            node_color = SOURCE_GAME_COLOR
            node_size = 28
            display_group = "Source Game"
        else:
            node_color = group_colors.get(group, default_color)
            node_size = 22 if group == "Game" else 12
            display_group = group

        if display_group not in grouped_nodes:
            grouped_nodes[display_group] = {
                "x": [],
                "y": [],
                "text": [],
                "hover": [],
                "size": [],
                "color": [],
            }

        grouped_nodes[display_group]["x"].append(x)
        grouped_nodes[display_group]["y"].append(y)
        grouped_nodes[display_group]["text"].append(label)
        grouped_nodes[display_group]["hover"].append(f"{display_group}: {label}")
        grouped_nodes[display_group]["size"].append(node_size)
        grouped_nodes[display_group]["color"].append(node_color)

    node_traces = []
    for display_group, data in grouped_nodes.items():
        node_traces.append(
            go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="markers+text",
                name=display_group,                 # appears in legend
                text=data["text"],
                textposition="top center",
                hovertext=data["hover"],
                hoverinfo="text",
                marker=dict(
                    size=data["size"],
                    line=dict(width=1, color="rgba(255,255,255,0.7)"),
                    color=data["color"],           # per-node colors
                ),
                showlegend=True,
            )
        )

    fig = go.Figure(
        data=[other_edge_trace, primary_edge_trace, *node_traces],
        layout=go.Layout(
            title=title,
            dragmode="pan",
            height=700,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,            # push legend below the plot area
                xanchor="center",
                x=0.5,
                font=dict(size=10),
            ),
            margin=dict(l=10, r=10, b=10, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig
