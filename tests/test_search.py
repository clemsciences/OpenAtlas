from flask import url_for

from openatlas import app
from openatlas.models.entity import Entity
from tests.base import TestBaseCase


class SearchTest(TestBaseCase):

    def test_search(self) -> None:
        with app.test_request_context():
            app.preprocess_request()  # type: ignore
            person = Entity.insert('E21', 'Waldo')
            person.begin_to = '2018-01-01'
            person.update()
            person.link('P131', Entity.insert('E82', 'Waldo alias'))
            object_ = Entity.insert('E18', 'Waldorf', 'place')
            object_.link('P1', Entity.insert('E41', 'Waldorf alias'))
            Entity.insert('E21', 'Waldo without date')
        with app.app_context():  # type: ignore
            self.app.post(url_for('search_index'), data={'global-term': ''})
            rv = self.app.post(url_for('search_index'), data={'global-term': 'wal',
                                                              'include_dateless': True,
                                                              'begin_year': -100, 'end_year': 3000})
            assert b'Waldo' in rv.data
            rv = self.app.post(url_for('search_index'), data={'term': 'wal', 'own': True})
            assert b'Waldo' not in rv.data
            data = {'term': 'do', 'classes': 'actor'}
            rv = self.app.post(url_for('search_index'), data=data)
            assert b'Waldo' in rv.data
            rv = self.app.post(url_for('search_index'), follow_redirects=True,
                               data={'term': 'x', 'begin_year': 2, 'end_year': -1})
            assert b'cannot start after' in rv.data
