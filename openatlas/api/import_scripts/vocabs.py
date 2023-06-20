from typing import Any, Optional

from flask import g

from openatlas.api.import_scripts.util import get_exact_match, vocabs_requests
from openatlas.models.entity import Entity
from openatlas.models.reference_system import ReferenceSystem
from openatlas.database.reference_system import ReferenceSystem as Db
from openatlas.models.type import Type


def import_vocabs_data(
        id_: str,
        form_data: dict[str, Any],
        details: dict[str, Any]) -> int:
    return len(fetch_top_level(id_, details, form_data))


def fetch_top_level(
        id_: str,
        details: dict[str, Any],
        form_data: dict[str, Any]) -> list[dict[str, Any]]:
    req = vocabs_requests(id_, 'topConcepts', {'lang': form_data['language']})
    count = []
    if ref := get_vocabs_reference_system(details):
        for entry in req['topconcepts']:
            hierarchy = Entity.insert(
                'type',
                entry['label'],
                f'Automatically imported from {details["title"]}')
            Type.insert_hierarchy(
                hierarchy,
                'custom', form_data['classes'],
                form_data['multiple'])
            entry['subs'] = import_children(
                entry['uri'],
                id_,
                form_data['language'],
                ref,
                hierarchy)
            count.append(entry)
    return count


def import_children(
        uri: str,
        id_: str,
        lang: str,
        ref: ReferenceSystem,
        super_: Optional[Entity],) -> list[dict[str, Any]]:
    req = vocabs_requests(id_, 'narrower', {'uri': uri, 'lang': lang})
    exact_match_id = get_exact_match().id
    children = []
    child = None
    for entry in req['narrower']:
        name = entry['uri'].rsplit('/', 1)[-1]
        if super_:
            child = Entity.insert(
                'type',
                get_pref_label(entry['prefLabel'], id_, entry['uri']))
            child.link('P127', super_)
            ref.link('P67', child, name, type_id=exact_match_id)
        entry['subs'] = import_children(entry['uri'], id_, lang, ref, child)
        children.append(entry)
    return children


def get_pref_label(label: str, id_: str, uri: str) -> str:
    if not label:
        req = vocabs_requests(id_, 'label', {'uri': uri})
        label = req['prefLabel']
    return label


def get_vocabs_reference_system(details: dict[str, Any],) -> ReferenceSystem:
    title = details['title']
    system = None
    for system_ in g.reference_systems.values():
        if system_.name == f'{title} vocabulary':
            system = system_
    if not system:
        system = ReferenceSystem.insert_system({
            'name': f'{title} vocabulary',
            'description': f'Import of {title} vocabulary (autogenerated)',
            'website_url': g.settings['vocabs_base_url'],
            'resolver_url': f"{details['conceptUri'].rsplit('/', 1)[0]}/"})
        Db.add_classes(system.id, ['type'])
    return system


def get_vocabularies():
    req = vocabs_requests(endpoint='vocabularies', parameter={'lang': 'en'})
    out = []
    for voc in req['vocabularies']:
        out.append(voc | fetch_vocabulary_details(voc['uri']))
    return out


def fetch_vocabulary_details(id_: str) -> dict[str, str]:
    data = vocabs_requests(id_, parameter={'lang': 'en'})
    return {
        'id': data['id'],
        'title': data['title'],
        'defaultLanguage': data['defaultLanguage'],
        'languages': data['languages'],
        'conceptUri':
            data['conceptschemes'][0]['uri'] if data['conceptschemes'] else ''}


