from collections import OrderedDict

import pytest
from django.contrib.auth.models import User

from model_mommy import mommy

from faker import Faker

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.test import force_authenticate

from api.views import APIUserList, APIUserDetail, ItemList, ItemDetail, BibList, BibDetail, MarcList, MarcDetail, \
    EResourceList, EResourceDetail, LocationList, LocationDetail, ItemTypesList, ItemTypesDetail, ItemStatusesList, \
    ItemStatusesDetail, CallnumbermatchesList, FirstItemPerLocationList, api_root

pytestmark = [
    pytest.mark.django_db
]

fake = Faker()

# Use the API extension of Django's RequestFactory
rf = APIRequestFactory()


class TestAPIRoot():

    def test_status_ok(self):
        request = rf.get('/')
        view = api_root
        response = view(request)
        assert response.status_code == 200

    def test_response_value(self):
        request = rf.get('/')
        view = api_root
        response = view(request)
        assert isinstance(response.data, OrderedDict)
        assert isinstance(response.data['catalogApi'], OrderedDict)
        assert response.data['catalogApi']['version'] == '1'
        assert isinstance(response.data['catalogApi']['_links'], OrderedDict)
        assert all(key in response.data['catalogApi']['_links'] for key in ('self', 'apiusers', 'bibs', 'marc', 'items',
                                                                            'eresources', 'locations', 'itemtypes',
                                                                            'itemstatuses', 'callnumbermatches',
                                                                            'firstitemperlocation'))
        assert 'serverTime' in response.data
        assert all(key in response.data['serverTime'] for key in ('currentTime', 'timezone', 'utcOffset'))

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = api_root
        response = view(request)
        assert response.status_code == 405


class TestAPIUserList():

    def test_status_ok(self):
        request = rf.get('/')
        view = APIUserList.as_view()
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    def test_status_forbidden(self):
        request = rf.get('/')
        view = APIUserList.as_view()
        response = view(request)
        assert response.status_code == 403

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = APIUserList.as_view()
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 405

    def test_thing(self):
        request = rf.get('/')
        view = APIUserList.as_view()
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)


class TestAPIUserDetail():

    def test_status_ok(self):
        request = rf.get('/')
        api_user_name = fake.profile()['username']
        mommy.make('api.APIUser', user__username=api_user_name)
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        view = APIUserDetail.as_view()
        response = view(request, id=api_user_name)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    def test_status_not_found(self):
        request = rf.get('/')
        api_user_name = fake.profile()['username']
        mommy.make('api.APIUser', user__username=api_user_name)
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        view = APIUserDetail.as_view()
        response = view(request, id='not_api_user_name')
        assert response.status_code == 404

    def test_status_forbidden(self):
        request = rf.get('/')
        api_user_name = fake.profile()['username']
        mommy.make('api.APIUser', user__username=api_user_name)
        view = APIUserDetail.as_view()
        response = view(request, id=api_user_name)
        assert response.status_code == 403

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        api_user_name = fake.profile()['username']
        mommy.make('api.APIUser', user__username=api_user_name)
        user = User.objects.create_user(username='user')
        force_authenticate(request, user=user)
        view = APIUserDetail.as_view()
        response = view(request, id=api_user_name)
        assert response.status_code == 405


class TestItemList():

    def test_status_ok(self):
        request = rf.get('/')
        view = ItemList.as_view()
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    # def test_response_dict(self):
    #     request = rf.get('/')
    #     view = ItemList.as_view()
    #     response = view(request)
    #     assert isinstance(response.data, OrderedDict)
    #     assert isinstance(response.data['catalogApi'], OrderedDict)
    #     assert response.data['catalogApi']['version'] == '1'
    #     assert isinstance(response.data['catalogApi']['_links'], OrderedDict)
    #     assert all(key in response.data['catalogApi']['_links'] for key in ('self', 'apiusers', 'bibs', 'marc', 'items',
    #                                                                         'eresources', 'locations', 'itemtypes',
    #                                                                         'itemstatuses', 'callnumbermatches',
    #                                                                         'firstitemperlocation'))
    #     assert 'serverTime' in response.data
    #     assert all(key in response.data['serverTime'] for key in ('currentTime', 'timezone', 'utcOffset'))

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = ItemList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestItemDetail():

    @pytest.mark.parametrize('item_id', ['450972300486'])
    def test_status_ok(self, item_id):
        request = rf.get('/')
        view = ItemDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['00000'])
    def test_status_not_found(self, item_id):
        request = rf.get('/')
        view = ItemDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['450972300486'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = ItemDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestBibList():

    def test_status_ok(self):
        request = rf.get('/')
        view = BibList.as_view()
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = BibList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestBibDetail():

    @pytest.mark.parametrize('item_id', ['420911802087'])
    def test_status_ok(self, item_id):
        view = BibDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['00000'])
    def test_status_not_found(self, item_id):
        view = BibDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 404

    # @pytest.mark.parametrize(('request_type', 'item_id'), [
    #     ('post', '420911802087'),
    #     ('patch', '420911802087'),
    #     ('put', '420911802087'),
    #     ('delete', '420911802087')
    # ])

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['420911802087'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = BibDetail.as_view()
        response = view(request, item_id)
        assert response.status_code == 405


class TestMarcList():

    def test_status_ok(self):
        view = MarcList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    def test_status_post_method_not_allowed(self):
        view = MarcList.as_view()
        request = rf.post('/')
        response = view(request)
        assert response.status_code == 405

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = BibDetail.as_view()
        response = view(request)
        assert response.status_code == 405


class TestMarcDetail():

    @pytest.mark.parametrize('item_id', ['420909507305'])
    def test_status_ok(self, item_id):
        view = MarcDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['00000'])
    def test_status_not_found(self, item_id):
        view = MarcDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['420909507305'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = MarcDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestEResourceList():

    def test_status_ok(self):
        view = EResourceList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = EResourceList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestEResourceDetail():

    @pytest.mark.parametrize('item_id', ['433792696897'])
    def test_status_ok(self, item_id):
        view = EResourceDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['00000'])
    def test_status_not_found(self, item_id):
        view = EResourceDetail.as_view()
        request = rf.get('/')
        response = view(request, id=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['433792696897'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = EResourceDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestLocationList():

    def test_status_ok(self):
        view = LocationList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = LocationList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestLocationDetail():

    @pytest.mark.parametrize('item_id', ['w4422'])
    def test_status_ok(self, item_id):
        view = LocationDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['a0'])
    def test_status_not_found(self, item_id):
        view = LocationDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['w4422'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = LocationDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestItemTypesList():

    def test_status_ok(self):
        view = ItemTypesList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = ItemTypesList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestItemTypesDetail():

    @pytest.mark.parametrize('item_id', ['43'])
    def test_status_ok(self, item_id):
        view = ItemTypesDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['0'])
    def test_status_not_found(self, item_id):
        view = ItemTypesDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['43'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = ItemTypesDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestItemStatusesList():

    def test_status_ok(self):
        view = ItemStatusesList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = ItemStatusesList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestItemStatusesDetail():

    @pytest.mark.parametrize('item_id', ['a'])
    def test_status_ok(self, item_id):
        view = ItemStatusesDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('item_id', ['zz'])
    def test_status_not_found(self, item_id):
        view = ItemStatusesDetail.as_view()
        request = rf.get('/')
        response = view(request, code=item_id)
        assert response.status_code == 404

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    @pytest.mark.parametrize('item_id', ['a'])
    def test_status_method_not_allowed(self, request_type, item_id):
        request = getattr(rf, request_type)('/')
        view = ItemStatusesDetail.as_view()
        response = view(request, id=item_id)
        assert response.status_code == 405


class TestCallnumbermatchesList():

    def test_status_ok(self):
        view = CallnumbermatchesList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, list)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = CallnumbermatchesList.as_view()
        response = view(request)
        assert response.status_code == 405


class TestFirstItemPerLocationList():

    def test_status_ok(self):
        view = FirstItemPerLocationList.as_view()
        request = rf.get('/')
        response = view(request)
        assert response.status_code == 200
        assert isinstance(response.data, OrderedDict)

    @pytest.mark.parametrize('request_type', ['post', 'patch', 'put', 'delete'])
    def test_status_method_not_allowed(self, request_type):
        request = getattr(rf, request_type)('/')
        view = FirstItemPerLocationList.as_view()
        response = view(request)
        assert response.status_code == 405


# @pytest.mark.parametrize('url, start_row, end_row', [
#     ('/marc/?035a[matches]=^\(OCoLC', 0, 19),
#     ('/marc/?035a[matches]=^\(OCoLC&offset=20', 20, 39),
# ])
# def test_marclist_response(url, start_row, end_row):
#     request = factory.get(url, format='json', content_type='application/json')
#     response = marclist_view(request)
#     response.render()
#     assert json.loads(response.content)['totalCount'] != 0
#     assert json.loads(response.content)['startRow'] == start_row
#     assert json.loads(response.content)['endRow'] == end_row


# @pytest.mark.parametrize('url, self_link, prev_link, next_link', [
#     ('/marc/?035a[matches]=^\(OCoLC',
#      "http://testserver/marc/?035a%5Bmatches%5D=%5E%5C%28OCoLC", None,
#      'http://testserver/marc/?035a%5Bmatches%5D=%5E%5C%28OCoLC&offset=20'),
#     ('/marc/?035a[matches]=^\(OCoLC&offset=20',
#      'http://testserver/marc/?035a%5Bmatches%5D=%5E%5C%28OCoLC&offset=20',
#      'http://testserver/marc/?035a%5Bmatches%5D=%5E%5C%28OCoLC&offset=0',
#      'http://testserver/marc/?035a%5Bmatches%5D=%5E%5C%28OCoLC&offset=40'),
# ])
# def test_marclist_links(url, self_link, prev_link, next_link):
#     request = factory.get(url, format='json', content_type='application/json')
#     response = marclist_view(request)
#     response.render()
#     response_content = json.loads(response.content)
#
#     assert response_content['_links']['self']['href'] == self_link
#     if prev_link is not None:
#         assert response_content['_links']['previous']['href'] == prev_link
#     if next_link is not None:
#         assert response_content['_links']['next']['href'] == next_link
