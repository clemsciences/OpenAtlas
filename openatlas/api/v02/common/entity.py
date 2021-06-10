from typing import Any, Dict, Tuple, Union

from flask import Response
from flask_restful import Resource, marshal

from openatlas.api.export.csv_export import ApiExportCSV
from openatlas.api.v02.resources.download import Download
from openatlas.api.v02.resources.geojson import Geojson
from openatlas.api.v02.resources.linked_places import LinkedPlaces
from openatlas.api.v02.resources.parser import entity_parser
from openatlas.api.v02.resources.util import get_entity_by_id
from openatlas.api.v02.templates.geojson import GeojsonTemplate
from openatlas.api.v02.templates.linked_places import LinkedPlacesTemplate


class GetEntity(Resource):  # type: ignore
    @staticmethod
    def get(id_: int) -> Union[Tuple[Resource, int], Response]:
        parser = entity_parser.parse_args()
        if parser['format'] == 'geojson':
            entity = GetEntity.get_geojson(id_)
            template = GeojsonTemplate.geojson_template()
            if parser['download']:
                return Download.download(data=entity, template=template, name=id_)
            return marshal(entity, template), 200
        if parser['export'] == 'csv':
            return ApiExportCSV.export_entity(get_entity_by_id(id_))
        entity = LinkedPlaces.get_entity(get_entity_by_id(id_), parser)
        template = LinkedPlacesTemplate.linked_places_template(parser['show'])
        if parser['download']:
            return Download.download(data=entity, template=template, name=id_)
        return marshal(entity, template), 200

    @staticmethod
    def get_geojson(id_: int) -> Dict[str, Any]:
        return Geojson.check_if_geometry(get_entity_by_id(id_))
