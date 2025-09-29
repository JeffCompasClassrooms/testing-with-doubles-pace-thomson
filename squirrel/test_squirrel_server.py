import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

# use @todo to cause pytest to skip that section
# handy for stubbing things out and then coming back later to finish them.
# @todo is heirarchical, and not sequential. Meaning that
# it will not skip 'peers' of other todos, only children.
todo = pytest.mark.skip(reason='TODO: pending spec')

class FakeRequest():
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    #this is not a 'makefile' like in c++ instead it 'makes' a response file
    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes('{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

#dummy client and dummy server to pass as params
#when creating SquirrelServerHandler
@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

@pytest.fixture
def dummy_server():
    return None

#a patch for mocking the DB initialize 
# function - this gets called a lot.
@pytest.fixture
def mock_db_init(mocker):
    return mocker.patch.object(SquirrelDB, '__init__', return_value=None)

@pytest.fixture
def mock_db_get_squirrels(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])


@pytest.fixture
def mock_db_get_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value='squirrel')

# patch SquirrelServerHandler to make our FakeRequest work correctly
@pytest.fixture(autouse=True)
def patch_wbufsize(mocker):
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')


# Fake Requests
@pytest.fixture
def fake_get_squirrels_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels')

@pytest.fixture
def fake_create_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='{"name":"Chippy","size":"small"}')

@pytest.fixture
def fake_bad_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Josh&')

@pytest.fixture
def fake_get_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels/1')

@pytest.fixture
def fake_update_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body='{"name":"Updated","size":"medium"}')

@pytest.fixture
def fake_delete_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

@pytest.fixture
def fake_invalid_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/invalid')

@pytest.fixture
def fake_post_invalid_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/invalid')

@pytest.fixture
def fake_put_invalid_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/invalid')

@pytest.fixture
def fake_delete_invalid_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/invalid')

@pytest.fixture
def fake_post_squirrels_with_id_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels/1')

@pytest.fixture
def fake_put_squirrels_without_id_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrels')

@pytest.fixture
def fake_delete_squirrels_without_id_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels')

# Additional DB method mocks
@pytest.fixture
def mock_db_create_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'createSquirrel', return_value=None)

@pytest.fixture
def mock_db_update_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)

@pytest.fixture
def mock_db_delete_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)

# Mock for getRequestData method
@pytest.fixture
def mock_get_request_data(mocker):
    return mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Test", "size": "small"})


#send_response, send_header and end_headers are inherited functions
#from the BaseHTTPRequestHandler. Go look at documentation here:
# https://docs.python.org/3/library/http.server.html
# Seriously. Go look at it. Pay close attention to what wfile is. :o)
# this fixture mocks all of the send____ that we use. 
# It is really just for convenience and cleanliness of code.
@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers


def describe_SquirrelServerHandler():

    def describe_handleSquirrelsIndex():
        def it_queries_db_for_squirrels(mocker, dummy_client, dummy_server):
            #setup
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])
            fake_get_squirrels_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels')
            
            #do the thing
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)

            #assert that the thing was done
            mock_get_squirrels.assert_called_once()

        def it_returns_200_status_code(fake_get_squirrels_request, dummy_client, dummy_server, mock_response_methods):
            
            #set up
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
                 
            # do the thing.
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            
            # assert methods calls and arguments
            mock_send_response.assert_called_once_with(200)

        def it_sends_json_content_type_header(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_returns_response_body_with_squirrels_json_data(fake_get_squirrels_request, dummy_client, dummy_server, mock_db_get_squirrels):
            #Do The thing:
            response = SquirrelServerHandler(fake_get_squirrels_request, dummy_client, dummy_server)
            #assert that the write function was called with a json version of the text 'squirrel'
            response.wfile.write.assert_called_once_with(bytes(json.dumps(['squirrel']), "utf-8"))

    def describe_handleSquirrelsRetrieve():
        """Tests for GET /squirrels/{id} - handleSquirrelsRetrieve method"""

        def it_queries_db_with_correct_id(mocker, fake_get_squirrel_request, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_returns_200_when_squirrel_found(fake_get_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(200)

        def it_sends_json_content_type_header_when_found(fake_get_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers_when_found(fake_get_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_writes_json_response_when_found(fake_get_squirrel_request, dummy_client, dummy_server, mock_db_get_squirrel):
            response = SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            response.wfile.write.assert_called_once_with(bytes(json.dumps('squirrel'), "utf-8"))

        def it_calls_handle404_when_squirrel_not_found(mocker, fake_get_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            SquirrelServerHandler(fake_get_squirrel_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_handleSquirrelsCreate():
        """Tests for POST /squirrels - handleSquirrelsCreate method"""

        def it_calls_getRequestData(mocker, fake_create_squirrel_request, dummy_client, dummy_server, mock_db_create_squirrel):
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Test", "size": "small"})
            SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
            mock_get_request_data.assert_called_once()

        def it_queries_db_to_create_squirrel_with_given_data_attributes(mocker, fake_create_squirrel_request, dummy_client, dummy_server):
            #setup.
            mock_db_create_squirrel = mocker.patch.object(SquirrelDB,'createSquirrel',return_value=None)
            mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Chippy", "size": "small"})

            #do the thing.
            SquirrelServerHandler(fake_create_squirrel_request,dummy_client,dummy_server)

            #assert the thing was done.
            mock_db_create_squirrel.assert_called_once_with('Chippy','small')

        def it_returns_201_status_code(fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(201)

        def it_calls_end_headers(fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

    def describe_handleSquirrelsUpdate():
        """Tests for PUT /squirrels/{id} - handleSquirrelsUpdate method"""

        def it_queries_db_first_to_check_squirrel_exists(mocker, fake_update_squirrel_request, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Updated", "size": "medium"})
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_calls_getRequestData_when_squirrel_found(mocker, fake_update_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Updated", "size": "medium"})
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_get_request_data.assert_called_once()

        def it_updates_squirrel_with_correct_data_when_found(mocker, fake_update_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Updated", "size": "medium"})
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_update_squirrel.assert_called_once_with('1', 'Updated', 'medium')

        def it_returns_204_when_squirrel_found(mocker, fake_update_squirrel_request, dummy_client, dummy_server, mock_response_methods):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Updated", "size": "medium"})
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(204)

        def it_calls_end_headers_when_found(mocker, fake_update_squirrel_request, dummy_client, dummy_server, mock_response_methods):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel', return_value=None)
            mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={"name": "Updated", "size": "medium"})
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_calls_handle404_when_squirrel_not_found(mocker, fake_update_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            SquirrelServerHandler(fake_update_squirrel_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_handleSquirrelsDelete():
        """Tests for DELETE /squirrels/{id} - handleSquirrelsDelete method"""

        def it_queries_db_first_to_check_squirrel_exists(mocker, fake_delete_squirrel_request, dummy_client, dummy_server):
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_get_squirrel.assert_called_once_with('1')

        def it_deletes_squirrel_when_found(mocker, fake_delete_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_delete_squirrel.assert_called_once_with('1')

        def it_returns_204_when_squirrel_found(mocker, fake_delete_squirrel_request, dummy_client, dummy_server, mock_response_methods):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(204)

        def it_calls_end_headers_when_found(mocker, fake_delete_squirrel_request, dummy_client, dummy_server, mock_response_methods):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel', return_value=None)
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_calls_handle404_when_squirrel_not_found(mocker, fake_delete_squirrel_request, dummy_client, dummy_server):
            mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            SquirrelServerHandler(fake_delete_squirrel_request, dummy_client, dummy_server)
            mock_handle404.assert_called_once()

    def describe_handle404():
        """Tests for error handling - handle404 method"""

        def it_returns_404_status_code(fake_invalid_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_invalid_request, dummy_client, dummy_server)
            mock_send_response.assert_called_once_with(404)

        def it_sends_text_plain_content_type_header(fake_invalid_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_invalid_request, dummy_client, dummy_server)
            mock_send_header.assert_called_once_with("Content-Type", "text/plain")

        def it_calls_end_headers(fake_invalid_request, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            SquirrelServerHandler(fake_invalid_request, dummy_client, dummy_server)
            mock_end_headers.assert_called_once()

        def it_writes_404_not_found_message(fake_invalid_request, dummy_client, dummy_server):
            response = SquirrelServerHandler(fake_invalid_request, dummy_client, dummy_server)
            response.wfile.write.assert_called_once_with(bytes("404 Not Found", "utf-8"))


