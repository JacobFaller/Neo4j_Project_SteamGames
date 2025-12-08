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

            if node_id not in G:
                G.add_node(
                    node_id,
                    label=props.get("name") or props.get("title") or group,
                    group=group,
                    role=key,  # <= this lets us distinguish g / other / tag
                )

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
    Custom layout for Q7:
      - role 'g'      -> center
      - role 'tag'    -> middle ring
      - role 'other'  -> outer ring
    """
    # Separate nodes by role (fallback to group if role missing)
    center_nodes = []
    tag_nodes = []
    other_nodes = []

    for n, attrs in G.nodes(data=True):
        role = attrs.get("role")  # g / other / tag in Q7
        group = attrs.get("group")

        if role == "g":
            center_nodes.append(n)
        elif role == "tag" or group == "Tag":
            tag_nodes.append(n)
        elif role == "other":
            other_nodes.append(n)
        else:
            other_nodes.append(n)

    pos = {}

    # Center: main game(s)
    for n in center_nodes:
        pos[n] = (0.0, 0.0)

    # Helper to place nodes on a circle of given radius
    def place_circle(nodes, radius):
        if not nodes:
            return
        step = 2 * math.pi / len(nodes)
        for i, n in enumerate(nodes):
            angle = i * step
            pos[n] = (radius * math.cos(angle), radius * math.sin(angle))

    # Tags in middle ring, similar games in outer ring
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
    primary_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("role") == "g"]

    primary_edge_x = []
    primary_edge_y = []
    other_edge_x = []
    other_edge_y = []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        # If either endpoint is the primary game → highlight
        if u in primary_nodes or v in primary_nodes:
            primary_edge_x += [x0, x1, None]
            primary_edge_y += [y0, y1, None]
        else:
            other_edge_x += [x0, x1, None]
            other_edge_y += [y0, y1, None]

    # Grey faint edges (normal ones)
    other_edge_trace = go.Scatter(
        x=other_edge_x,
        y=other_edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1, color="rgba(180,180,180,0.4)"),
    )

    # Highlighted edges (to the central game)
    primary_edge_trace = go.Scatter(
        x=primary_edge_x,
        y=primary_edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1, color="#00aaff"),  # light blue isch xD
    )

    # ---------- Nodes ----------
    group_colors = {
        "Game": "#ffcc00",       # highlight games
        "Publisher": "#ff7f0e",
        "Developer": "#1f77b4",
        "Genre": "#2ca02c",
        "Tag": "#d62728",
        "Language": "#9467bd",
    }
    default_color = "#1f77b4"

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node_id, attrs in G.nodes(data=True):
        x, y = pos[node_id]
        group = attrs.get("group", "Other")
        label = attrs.get("label", str(node_id))

        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{group}: {label}")
        node_color.append(group_colors.get(group, default_color))

        # Make Game nodes larger
        if group == "Game":
            node_size.append(22)
        else:
            node_size.append(12)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[t.split(": ", 1)[-1] for t in node_text],  # show only name
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_size,
            line=dict(width=1, color="rgba(255,255,255,0.7)"),
            color=node_color,
        ),
    )

    fig = go.Figure(
    data=[other_edge_trace, primary_edge_trace, node_trace],
    layout=go.Layout(
        title=title,
        height=700,
        showlegend=False,
        margin=dict(l=10, r=10, b=10, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig
