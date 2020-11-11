import json

from flask import Response
from flask_restful import Resource, marshal

from openatlas.api.v02.resources.parser import language_parser
from openatlas.models.content import Content
from openatlas.api.v02.templates.content import ContentTemplate


class GetContent(Resource):
    def get(self):
        parser = language_parser.parse_args()
        content = {'intro': Content.get_translation('intro_for_frontend', parser['lang']),
                   'contact': Content.get_translation('contact_for_frontend', parser['lang']),
                   'legal-notice': Content.get_translation('legal_notice_for_frontend',
                                                           parser['lang'])}
        if parser['download']:
            return Response(json.dumps(marshal(content, ContentTemplate.content_template())),
                            mimetype='application/json',
                            headers={
                                'Content-Disposition': 'attachment;filename=content_' + parser[
                                    'lang'] + '.json'})
        return marshal(content, ContentTemplate.content_template()), 200