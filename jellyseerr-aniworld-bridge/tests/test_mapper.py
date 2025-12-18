import unittest
from unittest.mock import MagicMock
from jellyseerr_aniworld_bridge.mapper import RequestMapper

class TestRequestMapper(unittest.TestCase):
    def test_map_request_to_show(self):
        # Mock AniWorldClientWrapper
        mock_aniworld_client = MagicMock()
        mock_aniworld_client.find_show.return_value = [{"name": "Test Show", "link": "/test-show"}]

        mapper = RequestMapper(mock_aniworld_client)

        # Sample Jellyseerr request
        request = {
            "media": {
                "name": "Test Show",
                "originalName": "Tèsutō Shō",
                "year": 2023,
                "mediaType": "tv"
            }
        }

        result = mapper.map_request_to_show(request)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Show")
        mock_aniworld_client.find_show.assert_called_once_with("Tèsutō Shō")

if __name__ == '__main__':
    unittest.main()
