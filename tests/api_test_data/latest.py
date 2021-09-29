test_latest = {'results': [{
    '@context': 'https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld',
    'type': 'FeatureCollection',
    'features': [{
        '@id': 'http://local.host/entity/122',
        'type': 'Feature',
        'crmClass': 'crm:E33 Linguistic Object',
        'systemClass': 'source',
        'properties': {'title': 'Silmarillion'},
        'description': None,
        'when': {
            'timespans': [{'start': {'earliest': 'None', 'latest': 'None'},
                           'end': {'earliest': 'None', 'latest': 'None'}}]},
        'types': None,
        'relations': None,
        'names': None,
        'links': None,
        'geometry': None,
        'depictions': None}]}, {
    '@context': 'https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld',
    'type': 'FeatureCollection',
    'features': [{
        '@id': 'http://local.host/entity/120',
        'type': 'Feature',
        'crmClass': 'crm:E18 Physical Thing',
        'systemClass': 'place',
        'properties': {'title': 'Mordor'},
        'description': [{'value': 'The heart of evil.'}],
        'when': {
            'timespans': [{'start': {'earliest': 'None', 'latest': 'None'},
                           'end': {'earliest': 'None', 'latest': 'None'}}]},
        'types': [{'identifier': 'http://local.host/api/0.2/entity/70',
                   'label': 'Boundary Mark', 'description': None,
                   'hierarchy': 'Place', 'value': None, 'unit': None}],
        'relations': [
            {'label': 'Boundary Mark',
             'relationTo': 'http://local.host/api/0.2/entity/70',
             'relationType': 'crm:P2 has type',
             'relationSystemClass': 'type',
             'relationDescription': None, 'type': None, 'when': {
                'timespans': [{'start': {'earliest': 'None', 'latest': 'None'},
                               'end': {'earliest': 'None',
                                       'latest': 'None'}}]}},
            {'label': 'Location of Mordor',
             'relationTo': 'http://local.host/api/0.2/entity/121',
             'relationType': 'crm:P53 has former or current location',
             'relationSystemClass': 'object_location',
             'relationDescription': None, 'type': None, 'when': {
                'timespans': [
                    {'start': {'earliest': 'None', 'latest': 'None'},
                     'end': {'earliest': 'None',
                             'latest': 'None'}}]}}],
        'names': None,
        'links': None,
        'geometry': {'type': 'GeometryCollection', 'geometries': []},
        'depictions': None}]}],
    'pagination': {
        'entities': 2,
        'entitiesPerPage': 20,
        'index': [{'page': 1, 'startId': 122}],
        'totalPages': 1}}
