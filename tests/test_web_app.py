import unittest
from unittest.mock import Mock, patch
from web_app import compare, Handler

INDEX = {'embedding_model': 'test', 'chunks': [
    {'id': 0, 'title': 'Source', 'url': 'https://example.com', 'text': 'retrieval evidence', 'embedding': [1.0, 0.0]},
    {'id': 1, 'title': 'Other', 'url': 'https://example.com/other', 'text': 'cooking', 'embedding': [0.0, 1.0]}]}


class WebTests(unittest.TestCase):
    @patch('web_app.rag.API')
    @patch('web_app.read_index', return_value=INDEX)
    def test_comparison_reuses_embedding_and_removes_vectors(self, read, api_type):
        api = api_type.return_value
        api.embed.return_value = [[1.0, 0.0]]
        result = compare({'question': 'retrieval', 'generate': False})
        self.assertEqual(set(result['results']), {'bm25', 'semantic', 'hybrid'})
        api.embed.assert_called_once()
        api.call.assert_not_called()
        self.assertNotIn('embedding', result['results']['hybrid'][0])

    @patch('web_app.rag.API', side_effect=ValueError('secret diagnostic'))
    @patch('web_app.read_index', return_value=INDEX)
    def test_api_failure_preserves_keywords_without_leaking_details(self, read, api):
        result = compare({'question': 'retrieval'})
        self.assertTrue(result['results']['bm25'])
        self.assertIn('retrieval', result['errors'])
        self.assertNotIn('secret diagnostic', str(result))

    @patch('web_app.rag.answer', return_value='Answer [1]')
    @patch('web_app.rag.API')
    @patch('web_app.read_index', return_value=INDEX)
    def test_answer_uses_hybrid_evidence(self, read, api_type, answer):
        api_type.return_value.embed.return_value = [[1.0, 0.0]]
        result = compare({'question': 'retrieval'})
        self.assertEqual(result['answer'], 'Answer [1]')
        self.assertEqual(answer.call_args.args[2][0]['id'], result['results']['hybrid'][0]['id'])

    def test_invalid_payloads(self):
        for payload in ({'question': ' '}, {'question': 'q', 'top_k': True}, {'question': 'q', 'top_k': 11}, {'question': 'q', 'generate': 'yes'}):
            with self.assertRaises(ValueError):
                compare(payload)

    def test_cross_origin_and_dns_rebinding_rejected(self):
        handler = Mock()
        handler.server.server_port = 8000
        for host, origin, allowed in [('127.0.0.1:8000', 'http://127.0.0.1:8000', True), ('evil.example:8000', None, False), ('127.0.0.1:8000', 'https://evil.example', False)]:
            handler.headers = {'Host': host, 'Origin': origin}
            self.assertEqual(Handler.trusted_request(handler), allowed)
