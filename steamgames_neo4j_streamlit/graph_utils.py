from pyvis.network import Network


def build_network(records, node_keys, rel_keys):
    """
    records: list of neo4j.Record
    node_keys: variable names that are nodes in the RETURN clause
    rel_keys: variable names that are relationships
    """
    net = Network(height="600px", width="100%", bgcolor="#0d1117", font_color="white")
    net.barnes_hut()

    seen_nodes = set()

    for rec in records:
        data = rec.data()  # dict: key -> Node / Relationship / None

        # Nodes
        for key in node_keys:
            node = data.get(key)
            if node is None:
                continue

            # neo4j.graph.Node expected
            node_id = node.id
            if node_id in seen_nodes:
                continue
            seen_nodes.add(node_id)

            labels = list(getattr(node, "labels", []))
            main_label = labels[0] if labels else key

            props = dict(node)
            title = props.get("name") or props.get("title") or main_label

            net.add_node(
                node_id,
                label=title,
                title=f"{main_label}: {title}",
                group=main_label,
            )

        # Relationships
        for key in rel_keys:
            rel = data.get(key)
            if rel is None:
                continue

            start_id = rel.start_node_id
            end_id = rel.end_node_id
            rel_type = rel.type

            net.add_edge(start_id, end_id, title=rel_type)

    return net
