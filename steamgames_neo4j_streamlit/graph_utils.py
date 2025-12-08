from pyvis.network import Network

def build_network(records, node_keys, rel_keys):
    net = Network(height="600px", width="100%", bgcolor="#0d1117", font_color="white")
    net.barnes_hut()

    seen = set()

    for r in records:
        data = r.data()

        # Add nodes
        for key in node_keys:
            node = data.get(key)
            if node is None:
                continue

            node_id = node.id
            if node_id not in seen:
                seen.add(node_id)

                label = list(node.labels)[0] if node.labels else "Node"
                title = node.get("name") or node.get("title") or label

                net.add_node(
                    node_id,
                    label=title,
                    title=f"{label}: {title}",
                    group=label,
                )

        # Add edges
        for key in rel_keys:
            rel = data.get(key)
            if rel:
                net.add_edge(rel.start_node_id, rel.end_node_id, title=rel.type)

    return net
