from typing import Any, Optional

from flask import g
from numpy import datetime64

from openatlas.api.resources.util import (
    flatten_list_and_remove_duplicates, get_linked_entities_id_api)
from openatlas.models.entity import Entity, Link


def get_search_values(
        category: str,
        parameter: dict[str, Any]) -> list[str | int | list[int]]:
    values = parameter["values"]
    match category:
        case "typeIDWithSubs":
            values = [[i] + g.types[i].get_sub_ids_recursive() for i in values]
        case "relationToID":
            values = flatten_list_and_remove_duplicates(
                [get_linked_entities_id_api(value) for value in values])
        case _:
            values = [
                value.lower() if isinstance(value, str) else value
                for value in values]
    return values


def search_entity(entity: Entity | Link, param: dict[str, Any]) -> bool:
    entity_values = value_to_be_searched(entity, param)
    operator_ = param['operator']
    search_values = param['search_values']
    logical_operator = param['logical_operator']
    is_comparable = param['is_comparable']

    if not entity_values and (operator_ == 'like' or is_comparable):
        return False

    if any(isinstance(i, list) for i in search_values):
        if logical_operator == 'or':
            search_values = flatten_list_and_remove_duplicates(search_values)
        else:
            bool_values = []
            for search_value in search_values:
                if operator_ == 'equal':
                    if logical_operator == 'and':
                        bool_values.append(bool(any(
                            item in entity_values for item in search_value)))
                if operator_ == 'notEqual':
                    if logical_operator == 'and':
                        bool_values.append(bool(not any(
                            item in entity_values for item in search_value)))
            return all(bool_values)
    bool_ = False
    # print(entity_values)
    # print(type(entity_values))
    # print(type(search_values))
    match operator_:
        case 'equal' if logical_operator == 'or':
            bool_ = bool(any(item in entity_values for item in search_values))
        case 'equal' if logical_operator == 'and':
            bool_ = bool(all(item in entity_values for item in search_values))
        case 'notEqual' if logical_operator == 'or':
            bool_ = bool(
                not any(item in entity_values for item in search_values))
        case 'notEqual' if logical_operator == 'and':
            bool_ = bool(
                not all(item in entity_values for item in search_values))
        case 'like' if logical_operator == 'or':
            bool_ = bool(any(
                item in value for item in search_values
                for value in entity_values))
        case 'like' if logical_operator == 'and':
            bool_ = bool(all(
                item in ' '.join(entity_values) for item in search_values))
        case 'greaterThan' if is_comparable and logical_operator == 'or':
            bool_ = bool(any(item < entity_values for item in search_values))
        case 'greaterThan' if is_comparable and logical_operator == 'and':
            if param['category'] == 'valueTypeID':
                test_bool = []
                for search_value in search_values:
                    test_dict = dict(entity_values)
                    if search_value[0] not in test_dict:
                        test_bool.append(False)
                        continue
                    test_bool.append(test_dict[search_value[0]] > search_value[1])
                print(test_bool)
                bool_ = bool(all(test_bool))
            else:
                bool_ = bool(all(item < entity_values for item in search_values))
        case 'greaterThanEqual' if is_comparable and logical_operator == 'or':
            bool_ = bool(any(item <= entity_values for item in search_values))
        case 'greaterThanEqual' if is_comparable and logical_operator == 'and':
            bool_ = bool(all(item <= entity_values for item in search_values))
        case 'lesserThan' if is_comparable and logical_operator == 'or':
            bool_ = bool(any(item > entity_values for item in search_values))
        case 'lesserThan' if is_comparable and logical_operator == 'and':
            bool_ = bool(all(item > entity_values for item in search_values))
        case 'lesserThanEqual' if is_comparable and logical_operator == 'or':
            bool_ = bool(any(item >= entity_values for item in search_values))
        case 'lesserThanEqual' if is_comparable and logical_operator == 'and':
            bool_ = bool(all(item >= entity_values for item in search_values))
    return bool_


def value_to_be_searched(
        entity: Entity, param: dict[str, Any]) \
        -> list[int | str | tuple[int, float]] | Optional[datetime64]:
    value: list[int | str | tuple[int, float]] | Optional[datetime64] = []
    match param['category']:
        case "entityID" | "relationToID":
            value = [entity.id]
        case "entityName":
            value = [entity.name.lower()]
        case "entityDescription" if entity.description:
            value = [entity.description.lower()]
        case "entityAliases":
            value = list(
                value.lower() for value in entity.aliases.values()
                if isinstance(value, str))
        case "entityCidocClass":
            value = [entity.cidoc_class.code.lower()]
        case "entitySystemClass":
            value = [entity.class_.name.lower()]
        case "typeName":
            value = [type_.name.lower() for type_ in entity.types]
        case "typeID" | "typeIDWithSubs":
            value = [type_.id for type_ in entity.types]
        case "beginFrom":
            value = entity.begin_from
        case "beginTo":
            value = entity.begin_to
        case "endFrom":
            value = entity.end_from
        case "endTo":
            value = entity.end_to
        case "valueTypeID":
            value = []
            for link_ in param['value_type_links']:
                if entity.id == link_.domain.id:
                    value.append((link_.range.id, float(link_.description)))
    return value
