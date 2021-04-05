import pytest
import urllib
from homescraper.providers import get_apartments
import homescraper.providers

casa_search_url = 'https://www.casa.it/affitto/residenziale?sortType=date_desc'
immobiliare_search_url = 'https://www.immobiliare.it/affitto-appartamenti/roma/?criterio=dataModifica&ordine=desc'
subito_search_url = 'https://www.subito.it/annunci-lazio/vendita/appartamenti/roma/roma/'


@pytest.mark.parametrize("search_url", [
    casa_search_url,
    immobiliare_search_url,
    subito_search_url,
])
def test_count(search_url, mocker):
    apts = get_apartments(search_url, 3)
    assert len(apts) == 3
    
    apts = get_apartments(search_url, 21)
    assert len(apts) == 21


@pytest.mark.parametrize("search_url", [
    casa_search_url,
    immobiliare_search_url,
    subito_search_url
])
def test_apartmenre_set_fields(search_url):
    apts = get_apartments(search_url, 3)
    assert len(apts) > 0
    for apt in apts:
        assert apt.url
        assert apt.url.startswith('http')

        assert apt.rooms is None or (apt.rooms > 0 and apt.rooms < 10)
        assert apt.mq is None or (apt.mq > 10)

        assert apt.image_url is None or apt.image_url.startswith('http')


def test_number_of_urlopen_calls_casa(mocker):
    page_load_spy = mocker.spy(homescraper.providers, 'get_http_url')

    apts = get_apartments(casa_search_url, 3)
    assert len(apts) == 3
    page_load_spy.assert_called_once()

    page_load_spy.reset_mock()
    apts = get_apartments(casa_search_url, 21)
    assert len(apts) == 21
    assert page_load_spy.call_count == 2


def test_number_of_urlopen_calls_immobiliare(mocker):
    page_load_spy = mocker.spy(homescraper.providers, 'get_http_url')

    apts = get_apartments(immobiliare_search_url, 3)
    assert len(apts) == 3
    page_load_spy.assert_called_once()

    page_load_spy.reset_mock()
    apts = get_apartments(immobiliare_search_url, 50)
    assert len(apts) == 50
    assert page_load_spy.call_count == 2


def test_number_of_urlopen_calls_subito(mocker):
    page_load_spy = mocker.spy(homescraper.providers, 'get_http_url')

    apts = get_apartments(subito_search_url, 3)
    assert len(apts) == 3
    page_load_spy.assert_called_once()

    page_load_spy.reset_mock()
    apts = get_apartments(subito_search_url, 21)
    assert len(apts) == 21
    assert page_load_spy.call_count == 1

