import os
import logging

from homescraper.config import parse_config
from homescraper.providers import get_apartments
from homescraper.exceptions import UnknownSearchProvider
from homescraper.db import ApartmentDb
from homescraper.notification import notify_new_apartment

_logger = logging.getLogger(__name__)

def scrape_apartments(config_path):
    queries, db_path, twilio = parse_config(config_path)
    _logger.info(f'Loaded {len(queries)} queries..')

    new_db = False
    if not os.path.exists(db_path):
        new_db = True

    db = ApartmentDb(db_path)

    new_apartments = []
    for q in queries:
        _logger.info('Searching new apartments for query "%s".. ' % q['name'])
        try:
            apartments = get_apartments(q['url'], q.get('count', 50))
            _logger.info(f'Returned {len(apartments)} apartments.. ')

            count = 0
            for apartment in apartments:
                if db.add_apartment(apartment):
                    new_apartments.append(apartment)
                    count += 1

            _logger.info(f'found {count} new apartments')
        except UnknownSearchProvider:
            _logger.info('skipping: unknown provider')

    if not new_db and len(new_apartments) < 3:
        for new_apt in new_apartments:
            notify_new_apartment(twilio['sid'], twilio['token'], twilio['from'], twilio['to'], new_apt)
