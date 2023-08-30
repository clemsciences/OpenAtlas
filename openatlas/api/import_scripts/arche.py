from typing import Any

import rdflib
import requests
from flask import flash, g
from requests import HTTPError, Response
from werkzeug.exceptions import abort

from openatlas import app
from openatlas.api.import_scripts.util import (
    get_exact_match, get_or_create_type, get_reference_system)
from openatlas.database.gis import Gis as Db_gis
from openatlas.database.reference_system import ReferenceSystem as Db
from openatlas.models.entity import Entity
from openatlas.models.imports import is_float
from openatlas.models.reference_system import ReferenceSystem
from openatlas.models.type import Type


def fetch_arche_data() -> dict[int, Any]:
    collections = {}
    for id_ in app.config['ARCHE']['collection_ids']:
        req = requests.get(
            f"{app.config['ARCHE']['base_url']}/api/{id_}/metadata",
            headers={'Accept': 'application/ld+json'}, timeout=60)
        try:
            if req:  # pragma: no cover
                collections[id_] = get_metadata(req.json())
                # collections[id_] = get_metadata_(n_triples_to_json(req))
        except HTTPError as http_error:  # pragma: no cover
            flash(f'ARCHE fetch failed: {http_error}', 'error')
            abort(404)
    return collections


def get_metadata(data: dict[str, Any]) -> dict[str, Any]:
    existing_ids = get_existing_ids()  # will not work, change method
    metadata = {}
    for collection in data['@graph']:
        if collection['@type'] == "n1:Collection":
            if collection["n1:hasFilename"] == "2_JPEGs":
                continue
            id_ = collection['@id'].replace('n0:', '')
            if id_ in existing_ids:
                continue

            collection_url = (data['@context']['n0'] + id_)
            metadata[collection_url] = {
                'collection_id': id_,
                'filename': collection['n1:hasFilename']}
    print(metadata)
    return metadata


def get_existing_ids():
    system = get_arche_reference_system()
    return [int(link_.description) for link_ in system.get_links('P67')]


def get_metadata_(data: dict[str, Any]) -> dict[str, Any]:
    system = get_arche_reference_system()
    existing_ids = \
        [int(link_.description) for link_ in system.get_links('P67')]
    metadata = {}
    for uri, node in data.items():
        print(node)
        for value in node.values():
            if '_metadata.json' in str(value[0]):
                json_ = requests.get(uri, timeout=60).json()
                image_url = get_linked_image(node['isMetadataFor'])
                image_id = int(image_url.rsplit('/', 1)[1])
                if image_id in existing_ids:
                    continue
                metadata[uri.rsplit('/', 1)[1]] = {
                    'image_id': image_id,
                    'image_link': image_url,
                    'image_link_thumbnail':
                        app.config['ARCHE']['thumbnail_url'] +
                        f"{image_url.replace('https://', '')}?width=1200",
                    'creator': json_['EXIF:Artist'],
                    'latitude': json_['EXIF:GPSLatitude'],
                    'longitude': json_['EXIF:GPSLongitude'],
                    'description': json_['XMP:Description']
                    if 'XMP:Description' in json_ else '',
                    'name': json_['IPTC:ObjectName'],
                    'license': json_['EXIF:Copyright'],
                    'date': json_['EXIF:CreateDate']}
    return metadata


def import_arche_data() -> int:
    count = 0
    person_types = get_or_create_person_types()
    arche_ref = get_reference_system('ARCHE')
    exact_match_id = get_exact_match().id
    for entries in fetch_arche_data().values():
        for item in entries.values():
            name = item['name']

            artifact = Entity.insert(
                'artifact',
                name.rsplit('.', 1)[0],
                item['description'])

            arche_ref.link(
                'P67',
                artifact,
                item['image_id'],
                type_id=exact_match_id)

            location = Entity.insert('object_location', f"Location of {name}")
            artifact.link('P53', location)
            if is_float(item['longitude']) and is_float(item['latitude']):
                Db_gis.insert(
                    shape='Point',
                    data={
                        'entity_id': location.id,
                        'name': name,
                        'description': '',
                        'type': 'centerpoint',
                        'geojson':
                            f'{{"type":"Point", "coordinates": '
                            f'[{item["longitude"]},'
                            f'{item["latitude"]}]}}'})

            production = Entity.insert(
                'production',
                f'Production of graffito from {name}')
            production.link('P108', artifact)

            file = Entity.insert('file', name, f"Created by {item['creator']}")
            file.link(
                'P2',
                get_or_create_type(
                    get_hierarchy_by_name('License'),
                    item['license']))
            filename = f"{file.id}.{name.rsplit('.', 1)[1].lower()}"
            open(str(
                app.config['UPLOAD_DIR'] / filename), "wb", encoding='utf-8') \
                .write(requests.get(
                item['image_link_thumbnail'],
                timeout=60).content)
            file.link('P67', artifact)

            creator = get_or_create_person(
                item['creator'],
                person_types['photographer_type'])

            creation = Entity.insert(
                'creation',
                f'Creation of photograph from {name}')
            creation.update({'attributes': {'begin_from': item['date']}})
            creation.link('P94', file)
            creation.link('P14', creator)

            count += 1
    return count


def get_linked_image(data: list[dict[str, Any]]) -> str:
    return [image['__uri__'] for image in data
            if str(image['mime'][0]) == 'image/jpeg'][0]


def get_hierarchy_by_name(name: str) -> Type:
    for type_id in g.types:
        if g.types[type_id].name == name:
            if not g.types[type_id].root:
                return g.types[type_id]
    abort(404)


def get_or_create_person(name: str, relevance: Type) -> Entity:
    for entity in Entity.get_by_cidoc_class('E21'):
        if entity.name == name:
            return entity
    entity = Entity.insert(
        'person',
        name,
        'Automatically created by ARCHE import')
    entity.link('P2', relevance)
    return entity


def get_or_create_person_types() -> dict[str, Any]:
    hierarchy: Entity = get_hierarchy_by_name('Relevance')
    if not hierarchy:
        hierarchy = Entity.insert('type', 'Relevance')
        Type.insert_hierarchy(hierarchy, 'custom', ['person'], True)
    return {
        'photographer_type': get_or_create_type(hierarchy, 'Photographer'),
        'artist_type': get_or_create_type(hierarchy, 'Graffito artist')}


def get_arche_reference_system() -> ReferenceSystem:
    system = None
    for system_ in g.reference_systems.values():
        if system_.name == 'ARCHE':
            system = system_
    if not system:
        system = ReferenceSystem.insert_system({
            'name': 'ARCHE',
            'description': 'ARCHE by ACDH-CH (autogenerated)',
            'website_url': 'https://arche.acdh.oeaw.ac.at/',
            'resolver_url':
                f"{app.config['ARCHE']['base_url']}browser/oeaw_detail/"})
    if 'artifact' not in system.classes:
        Db.add_classes(system.id, ['artifact'])
    return system


# Script from
# https://acdh-oeaw.github.io/arche-docs/aux/rdf_compacting.html
def n_triples_to_json(req: Response) -> dict[str, Any]:
    context = get_arche_context()
    data = rdflib.Graph()
    data.parse(data=req.text, format="nt")

    # create Python-native data model based on dictionaries
    nodes: dict[str, Any] = {}
    for (sbj, prop, obj) in data:
        sbj = str(sbj)
        prop = str(prop)
        # skip RDF properties for which we don't know the mapping
        if prop not in context:
            continue

        # map prop name according to the context
        prop = context[prop]

        # if the triple points to another node in the graph,
        # maintain the reference
        if not isinstance(obj, rdflib.term.Literal):
            if str(obj) not in nodes:
                nodes[str(obj)] = {'__uri__': str(obj)}
            obj = nodes[str(obj.toPython())]

        # manage the data
        if sbj not in nodes:
            nodes[sbj] = {'__uri__': sbj}
        if prop not in nodes[sbj]:
            nodes[sbj][prop] = []
        nodes[sbj][prop].append(
            obj if not isinstance(obj, rdflib.term.Literal)
            else obj.toPython())
    return nodes


def get_arche_context() -> dict[str, Any]:
    context = requests.get(
        'https://arche.acdh.oeaw.ac.at/api/describe',
        headers={'Accept': 'application/json'}, timeout=60)
    result: dict[str, Any] = context.json()['schema']
    # Adding isMetadataFor because it is not in /describe
    result['isMetadataFor'] = \
        'https://vocabs.acdh.oeaw.ac.at/schema#isMetadataFor'
    # Flip the context so it's uri->shortName
    return {v: k for k, v in result.items() if isinstance(v, str)}