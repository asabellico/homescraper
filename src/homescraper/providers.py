from bs4 import BeautifulSoup
from furl import furl
import re

from homescraper.datatypes import RawApartment
from homescraper.exceptions import UnknownSearchProvider
from homescraper.exceptions import PageNotFound
from homescraper.http import get_http_url

import logging
_logger = logging.getLogger(__name__)


def get_apartments(search_url, count):
    if 'immobiliare.it' in search_url:
        raw_apartments = get_apartments_immobiliare(search_url, count)

    elif 'subito.it' in search_url:
        raw_apartments = get_apartments_subito(search_url, count)

    elif 'casa.it' in search_url:
        raw_apartments = get_apartments_casa(search_url, count)

    else:
        raise UnknownSearchProvider('Unknown search provider')

    apartments = []
    for raw_apt in raw_apartments:
        apartments.append(raw_apt.to_apartment())

    return apartments


def get_elem_by_content(item, content, cl=None, item_type=None):
    filtered = item
    if cl:
        filtered = filtered.find_all(class_=cl)
    if item_type:
        filtered = filtered.find_all(item_type)

    for subitem in filtered:
        if re.match(content, subitem.get_text()):
            return subitem

    return None


def get_apartments_casa(search_url, count):
    raw_apartments = []
    visited_urls = set()

    page = 0
    while True:
        try:
            page += 1
            paginated_search_url = furl(search_url)
            paginated_search_url.args['page'] = page
            _logger.debug(f'[casa.it] Loading page {paginated_search_url}')
            html = get_http_url(paginated_search_url.url)
        except PageNotFound:
            _logger.debug('[casa.it] Page not found.. returning found apartments..')
            break
        search_content = BeautifulSoup(html, 'html.parser')

        apartment_items = search_content.find_all('article', class_='srp-card')
        _logger.debug(f'[casa.it] Page seems to contain {len(apartment_items)} items')
        for apartment_item in apartment_items:
            # retrive raw string data
            url = apartment_item.find('a').attrs['href']
            if not url:
                _logger.debug('Skipping apartment with no URL detected..')
                continue
            url = 'https://casa.it' + url

            # break loop if already added this url (casa.it do not return 404 when a page do not exist, 
            # this is the only way to check..)
            if url in visited_urls:
                _logger.debug('[casa.it] Already visited apartment URL, returning')
                return raw_apartments
            visited_urls.add(url)

            # parse rawapartment
            new_raw_apt = RawApartment(url = url)
            new_raw_apt.title = apartment_item.select('.casaAdTitle a')[0].get_text()
            price_item = get_elem_by_content(apartment_item, '.*€.*', item_type='p')
            if price_item:
                new_raw_apt.price = price_item.get_text()
            mq_item = get_elem_by_content(apartment_item, '.*mq.*', item_type='li')
            if mq_item:
                new_raw_apt.mq = mq_item.get_text()
            rooms_item = get_elem_by_content(apartment_item, '.*locali.*', item_type='li')
            if rooms_item:
                new_raw_apt.rooms = rooms_item.get_text()
            new_raw_apt.description = apartment_item.find('p', class_='decription').get_text()
            new_raw_apt.image_url = apartment_item.find('img').attrs['data-src']
            privato_item = apartment_item.find(title='privato')
            if privato_item:
                new_raw_apt.privato = 'Privato' in str(privato_item)
            raw_apartments.append(new_raw_apt)
            _logger.debug(f'[casa.it] parsed new raw apartment: {new_raw_apt.url}')

            if len(raw_apartments) >= count:
                return raw_apartments

    return raw_apartments


def get_apartments_immobiliare(search_url, count):
    raw_apartments = []

    page = 0
    while True:
        try:
            page += 1
            paginated_search_url = furl(search_url)
            paginated_search_url.args['pag'] = page
            _logger.debug(f'[immobiliare.it] Loading page {paginated_search_url.url}')
            html = get_http_url(paginated_search_url.url)
        except PageNotFound:
            _logger.debug('[immobiliare.it] Page not found.. returning found apartments..')
            break
        search_content = BeautifulSoup(html, 'html.parser')

        apartment_items = search_content.find_all(class_='listing-item')
        _logger.debug(f'[immobiliare.it] Page seems to contain {len(apartment_items)} items')
        for apartment_item in apartment_items:
            # retrive raw string data
            url_item = apartment_item.find('a', id=re.compile('link_ad_.*'))
            if url_item:
                url = url_item.attrs['href']
            else:
                url = None

            if not url:
                _logger.debug('Skipping apartment with no URL detected..')
                continue

            # parse rawapartment
            new_raw_apt = RawApartment(url = url)
            new_raw_apt.title = apartment_item.find('a', id=re.compile('link_ad_.*')).get_text()
            new_raw_apt.price = apartment_item.find(class_='lif__pricing').get_text()
            mq_child = get_elem_by_content(apartment_item, '^superficie$', cl='lif__text')
            if mq_child:
                new_raw_apt.mq = mq_child.parent.find('span').get_text()
            descr_item = apartment_item.find('p', class_='descrizione__truncate')
            if descr_item:
                new_raw_apt.description = descr_item.get_text()
            image_item = apartment_item.find('img', class_='no-image')
            if image_item:
                new_raw_apt.image_url = image_item.attrs.get('src')
            raw_apartments.append(new_raw_apt)
            _logger.debug(f'[immobiliare.it] parsed new raw apartment: {new_raw_apt.url}')

            if len(raw_apartments) >= count:
                return raw_apartments

    return raw_apartments


def get_apartments_subito(search_url, count):
    raw_apartments = []
    page = 0

    while True:
        try:
            page += 1
            paginated_search_url = furl(search_url)
            paginated_search_url.args['o'] = page
            _logger.debug(f'[subito.it] Loading page {paginated_search_url.url}')
            html = get_http_url(paginated_search_url.url)
        except PageNotFound:
            _logger.debug('[subito.it] Page not found.. returning found apartments..')
            break
        search_content = BeautifulSoup(html, 'html.parser')

        apartment_items = search_content.find_all(class_=re.compile('AdItemBigCard_card__.*'))
        if not apartment_items:
            break

        _logger.debug(f'[subito.it] Page seems to contain {len(apartment_items)} items')
        for apartment_item in apartment_items:
            # retrive raw string data
            url = apartment_item.find('a', class_=re.compile('AdItemBigCard_link__.*')).attrs['href']
            if not url:
                _logger.debug('Skipping apartment with no URL detected..')
                continue

            # parse rawapartment
            new_raw_apt = RawApartment(url = url)
            title_item = apartment_item.find('h2', class_=re.compile('ItemTitle_item-title__.*'))
            if title_item:
                new_raw_apt.title = title_item.get_text()
            price_item = apartment_item.find(class_=re.compile('classes_price__.*'))
            if price_item:
                new_raw_apt.price = price_item.get_text()
            mq_item = apartment_item.find(class_='classes_info__3ut5r')
            if mq_item:
                new_raw_apt.mq = mq_item.get_text()
            rooms_item = get_elem_by_content(apartment_item, '.*locali.*', cl='classes_info__3ut5r')
            if rooms_item:
                new_raw_apt.rooms = rooms_item.get_text()
            if apartment_item.find('img'):
                img_url = apartment_item.find('img').attrs['src']
                if 'bigcardimages' in img_url:
                    new_raw_apt.image_url = img_url

            raw_apartments.append(new_raw_apt)
            _logger.debug(f'[subito.it] parsed new raw apartment: {new_raw_apt.url}')

            if len(raw_apartments) >= count:
                return raw_apartments

    return raw_apartments