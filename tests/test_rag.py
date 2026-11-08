import unittest
from unittest.mock import Mock
from rag import PageText, bm25, chunk_text, fuse, normalize, search, answer


class RetrievalTests(unittest.TestCase):
    def test_bm25_prefers_keyword_match(self):
        scores = bm25('retrieval', ['retrieval retrieval augmented generation', 'cooking soup'])
        self.assertGreater(scores[0], scores[1])
        self.assertEqual(scores[1], 0)

    def test_chunks_overlap_without_losing_tail(self):
        self.assertEqual(list(chunk_text('a b c d e f g', 4, 1)), ['a b c d', 'd e f g'])
        with self.assertRaises(ValueError):
            list(chunk_text('text', 2, 2))

    def test_fusion_rewards_agreement(self):
        scores = fuse([[0, 1], [2, 1]])
        self.assertEqual(max(scores, key=scores.get), 1)

    def test_semantic_search_finds_synonym_without_keyword(self):
        api = Mock()
        api.embed.return_value = [[1.0, 0.0]]
        index = {'embedding_model': 'test', 'chunks': [
            {'text': 'automobile', 'embedding': [1.0, 0.0]},
            {'text': 'car insurance', 'embedding': [0.0, 1.0]}]}
        self.assertEqual(search(index, 'car', api, 'semantic')[0]['text'], 'automobile')
        self.assertEqual(search(index, 'car', mode='bm25')[0]['text'], 'car insurance')
        self.assertEqual(search(index, 'unknown', mode='bm25'), [])

    def test_empty_query_and_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            search({}, ' ')
        api = Mock()
        api.embed.return_value = [[1, 0]]
        with self.assertRaises(ValueError):
            search({'embedding_model': 'test', 'chunks': [{'text': 'a', 'embedding': [1]}]}, 'a', api)

    def test_normalization(self):
        self.assertEqual(normalize([3, 4]), [0.6, 0.8])
        with self.assertRaises(ValueError):
            normalize([0, 0])

    def test_html_removes_navigation_and_scripts(self):
        parser = PageText()
        parser.feed('<title>Title</title><nav>Menu</nav><script>secret()</script><p>Evidence</p>')
        self.assertIn('Evidence', parser.parts)
        self.assertNotIn('Menu', parser.parts)
        self.assertNotIn('secret()', parser.parts)

    def test_no_evidence_does_not_call_llm(self):
        api = Mock()
        self.assertIn('No matching', answer(api, 'question', []))
        api.call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
