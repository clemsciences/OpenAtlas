from typing import Any, Dict, List, Tuple, Union

from flask import Response, g, url_for
from flask_restful import Resource, marshal

from openatlas.api.resources.parser import default
from openatlas.api.resources.resolve_endpoints import download
from openatlas.api.templates.nodes_overview import NodesOverviewTemplate
from openatlas.models.entity import Entity
from openatlas.models.node import Node


class GetNodeOverview(Resource):  # type: ignore

    def get(self) -> Union[Tuple[Resource, int], Response]:
        parser = default.parse_args()
        node = {"types": GetNodeOverview.get_node_overview()}
        template = NodesOverviewTemplate.node_overview_template()
        if parser['download']:
            return download(node, template, 'types')
        return marshal(node, template), 200

    @staticmethod
    def get_node_overview() -> Dict[str, Dict[Entity, str]]:
        nodes: Dict[str, Any] = {
            'standard': {},
            'custom': {},
            'places': {},
            'value': {}}
        for node in g.nodes.values():
            if node.root:
                continue
            type_ = 'custom'
            if node.class_.name == 'administrative_unit':
                type_ = 'places'
            elif node.standard:
                type_ = 'standard'
            elif node.value_type:
                type_ = 'value'
            nodes[type_][node.name] = GetNodeOverview.walk_tree(
                Node.get_nodes(node.name))
        return nodes

    @staticmethod
    def walk_tree(nodes: List[int]) -> List[Dict[str, Any]]:
        items = []
        for id_ in nodes:
            item = g.nodes[id_]
            items.append({
                'id': item.id,
                'url': url_for('api.entity', id_=item.id, _external=True),
                'label': item.name.replace("'", "&apos;"),
                'children': GetNodeOverview.walk_tree(item.subs)})
        return items
