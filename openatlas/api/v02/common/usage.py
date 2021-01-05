from typing import Tuple, Union

from flasgger import swag_from
from flask import Response, url_for
from flask_cors import cross_origin
from flask_restful import Resource, marshal

from openatlas import app
from openatlas.api.v02.templates.usage import UsageTemplate
from openatlas.util.util import api_access


class ShowUsage(Resource):  # type: ignore
    @api_access()  # type: ignore
    @cross_origin(origins=app.config['CORS_ALLOWANCE'], methods=['GET'])
    @swag_from("../swagger/usage.yml", endpoint="usage")
    def get(self) -> Union[Tuple[Resource, int], Response]:
        usage = {
            'message': 'The path you entered is not correct. Please confer: ' + url_for(
                'flasgger.apidocs', _external=True),
            'examples':
                {'entity': url_for('entity', id_=23, _external=True),
                 'code': url_for('code', code='actor', _external=True),
                 'class': url_for('class', class_code='E18', _external=True),
                 'query': url_for('query', classes='E18', items='actor', entities=23,
                                  _external=True),
                 'latest': url_for('latest', latest='30', _external=True),
                 'node_entities': url_for('node_entities', id_=23, _external=True),
                 'node_entities_all': url_for('node_entities_all', id_=23, _external=True),
                 'subunit': url_for('subunit', id_=23, _external=True),
                 'subunit_hierarchy': url_for('subunit_hierarchy', id_=23, _external=True)}}
        template = UsageTemplate.usage_template()
        return marshal(usage, template), 200