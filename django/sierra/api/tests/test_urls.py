import pytest

from django.core.urlresolvers import resolve


@pytest.mark.parametrize('url, view_name', [
    ('/api/v1/', 'api_root'),
    ('/api/v1/apiusers/', 'APIUserList'),
    ('/api/v1/apiusers/0', 'APIUserDetail'),
    ('/api/v1/items/', 'ItemList'),
    ('/api/v1/items/000000', 'ItemDetail'),
    ('/api/v1/bibs/', 'BibList'),
    ('/api/v1/bibs/000000', 'BibDetail'),
    ('/api/v1/marc/', 'MarcList'),
    ('/api/v1/marc/000000', 'MarcDetail'),
    ('/api/v1/eresources/', 'EResourceList'),
    ('/api/v1/eresources/0000000', 'EResourceDetail'),
    ('/api/v1/locations/', 'LocationList'),
    ('/api/v1/locations/aaaa0000', 'LocationDetail'),
    ('/api/v1/itemtypes/', 'ItemTypesList'),
    ('/api/v1/itemtypes/aaaa0000', 'ItemTypesDetail'),
    ('/api/v1/itemstatuses/', 'ItemStatusesList'),
    ('/api/v1/itemstatuses/aaaa0000', 'ItemStatusesDetail'),
    ('/api/v1/callnumbermatches/', 'CallnumbermatchesList'),
    ('/api/v1/firstitemperlocation/', 'FirstItemPerLocationList')
])
def test_urls(url, view_name):
    url = resolve(url)
    assert url.func.func_name == view_name
