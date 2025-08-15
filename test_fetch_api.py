import pytest
from fetch import get_ai_newsletters
from unittest.mock import MagicMock, patch
import fetch

class MockTqdm:
    """Mock tqdm to act as a passthrough context manager."""
    def __init__(self, *args, **kwargs):
        self.total = kwargs.get('total', 0)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def update(self, n=1):
        pass

class DummyMessages:
    def __init__(self, messages_data=None):
        self._messages_data = messages_data or []
    def list(self, userId, q):
        # Simulate filtering by 'from:' and 'to:' in the query string
        messages = []
        for msg in self._messages_data:
            # Simple filter simulation
            if 'from:' in q:
                from_filter = q.split('from:')[1].split()[0]
                if from_filter not in msg.get('from', ''):
                    continue
            if 'to:' in q:
                to_filter = q.split('to:')[1].split()[0]
                if to_filter not in msg.get('to', ''):
                    continue
            messages.append({'id': msg['id']})
        return MagicMock(execute=MagicMock(return_value={'messages': messages}))
    def get(self, userId, id, format):
        # Find the message by ID
        msg = next((m for m in self._messages_data if m['id'] == id), {})
        headers = []
        if 'subject' in msg:
            headers.append({'name': 'Subject', 'value': msg['subject']})
        if 'date' in msg:
            headers.append({'name': 'Date', 'value': msg['date']})
        if 'from' in msg:
            headers.append({'name': 'From', 'value': msg['from']})
        if 'to' in msg:
            headers.append({'name': 'To', 'value': msg['to']})
        return MagicMock(execute=MagicMock(return_value={
            'payload': {
                'headers': headers,
                'body': {'data': b'VGVzdCBib2R5'}  # 'Test body' in base64
            }
        }))

class DummyUsers:
    def __init__(self, messages_data):
        self._messages = DummyMessages(messages_data)
    def messages(self):
        return self._messages

class DummyService:
    def __init__(self, messages_data):
        self._users = DummyUsers(messages_data)
    def users(self):
        return self._users

def test_get_ai_newsletters_success(monkeypatch):
    # Simulate two messages
    messages_data = [
        {'id': '1', 'subject': 'Test 1', 'date': 'Mon, 1 Jan 2024 10:00:00 +0000', 'from': 'sender1@example.com', 'to': 'me@example.com'},
        {'id': '2', 'subject': 'Test 2', 'date': 'Tue, 2 Jan 2024 10:00:00 +0000', 'from': 'sender2@example.com', 'to': 'me@example.com'},
    ]
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = DummyService(messages_data)
    newsletters = get_ai_newsletters(service, days=1)
    assert len(newsletters) == 2
    assert newsletters[0]['subject'] == 'Test 1'
    assert newsletters[1]['subject'] == 'Test 2'

def test_get_ai_newsletters_no_messages(monkeypatch):
    messages_data = []
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = DummyService(messages_data)
    newsletters = get_ai_newsletters(service, days=1)
    assert newsletters == []

def test_get_ai_newsletters_api_error(monkeypatch):
    class ErrorMessages:
        def list(self, userId, q):
            raise Exception('API error')
        def get(self, userId, id, format):
            raise Exception('Should not be called')
    class ErrorUsers:
        def messages(self):
            return ErrorMessages()
    class ErrorService:
        def users(self):
            return ErrorUsers()
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = ErrorService()
    # Now with error handling, API errors return empty list instead of raising
    newsletters = get_ai_newsletters(service, days=1)
    assert newsletters == []

def test_get_ai_newsletters_from_and_to_filters(monkeypatch):
    messages_data = [
        {'id': '1', 'subject': 'Test 1', 'date': 'Mon, 1 Jan 2024 10:00:00 +0000', 'from': 'sender1@example.com', 'to': 'me@example.com'},
        {'id': '2', 'subject': 'Test 2', 'date': 'Tue, 2 Jan 2024 10:00:00 +0000', 'from': 'sender2@example.com', 'to': 'you@example.com'},
    ]
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = DummyService(messages_data)
    newsletters = get_ai_newsletters(service, days=1, from_email='sender1@example.com', to_email='me@example.com')
    assert len(newsletters) == 1
    assert newsletters[0]['subject'] == 'Test 1'

def test_get_ai_newsletters_missing_headers(monkeypatch):
    # Simulate messages with missing headers
    messages_data = [
        {'id': '1'},  # Message with no headers
        {'id': '2', 'subject': 'Test 2', 'date': 'Tue, 2 Jan 2024 10:00:00 +0000'},  # Missing 'from' and 'to'
    ]
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = DummyService(messages_data)
    newsletters = get_ai_newsletters(service, days=1)
    assert len(newsletters) == 2
    # First message will have default values
    assert newsletters[0]['subject'] == 'No Subject'
    assert newsletters[0]['sender'] == 'Unknown Sender'
    # Second message has some values
    assert newsletters[1]['subject'] == 'Test 2'
    assert newsletters[1]['sender'] == 'Unknown Sender'

def test_get_ai_newsletters_no_label(monkeypatch):
    # Simulate messages with different senders
    messages_data = [
        {'id': '1', 'subject': 'NoLabel 1', 'date': 'Mon, 1 Jan 2024 10:00:00 +0000', 'from': 'foo@example.com', 'to': 'me@example.com'},
        {'id': '2', 'subject': 'NoLabel 2', 'date': 'Tue, 2 Jan 2024 10:00:00 +0000', 'from': 'bar@example.com', 'to': 'me@example.com'},
    ]
    captured_query = {}
    class DummyMessagesNoLabel:
        def list(self, userId, q):
            captured_query['q'] = q
            return MagicMock(execute=MagicMock(return_value={'messages': [{'id': m['id']} for m in messages_data]}))
        def get(self, userId, id, format):
            msg = next(m for m in messages_data if m['id'] == id)
            return MagicMock(execute=MagicMock(return_value={
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': msg['subject']},
                        {'name': 'Date', 'value': msg['date']},
                        {'name': 'From', 'value': msg['from']},
                        {'name': 'To', 'value': msg['to']},
                    ],
                    'body': {'data': b'VGVzdCBib2R5'}
                }
            }))
    class DummyUsersNoLabel:
        def messages(self):
            return DummyMessagesNoLabel()
    class DummyServiceNoLabel:
        def users(self):
            return DummyUsersNoLabel()
    monkeypatch.setattr(fetch, 'tqdm', MockTqdm)
    service = DummyServiceNoLabel()
    newsletters = get_ai_newsletters(service, days=1, label=None)
    assert len(newsletters) == 2
    # Verify no label in the query
    assert 'label:' not in captured_query['q']
    assert 'after:' in captured_query['q']