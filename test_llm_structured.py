"""Offline OpenRouter structured-output tests."""
import json
import os
import unittest
from unittest.mock import patch

import agent_reviewer
from decision_engine import PREFERENCES, parse_objective


class FakeResponse:
    headers = {"Content-Length": "0"}

    def __init__(self, content):
        self.body = json.dumps({
            "choices": [{"message": {"content": content}}]
        }).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return self.body


class StructuredOutputTests(unittest.TestCase):

    def review(self, response_text):
        objective = "Cultural programming"
        intent = parse_objective(objective)["primary"]
        formats = list(PREFERENCES[intent][:3])

        env = {
            "ATLAS_LLM_URL": "https://openrouter.ai/api/v1/chat/completions",
            "ATLAS_LLM_MODEL": "openrouter/free",
            "ATLAS_LLM_API_KEY": ""
        }

        branches = {"movie": [], "brand": [], "place": []}

        with patch.dict(os.environ, env), \
             patch.object(agent_reviewer, "eligible_formats", return_value=formats), \
             patch.object(agent_reviewer.urllib.request, "urlopen",
                          return_value=FakeResponse(response_text)) as request:

            result = agent_reviewer.review_formats(
                {"name": "Nils Frahm"},
                branches,
                "Madrid",
                objective
            )

        payload = json.loads(request.call_args.args[0].data.decode())
        return result, payload, formats

    def test_structured_response(self):
        objective = "Cultural programming"
        formats = list(PREFERENCES[parse_objective(objective)["primary"]][:3])

        (choice, status), payload, formats = self.review(
            json.dumps({"formats": formats})
        )

        self.assertEqual(status, "validated")
        self.assertEqual(choice, formats)
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        self.assertTrue(payload["provider"]["require_parameters"])
        self.assertGreater(payload["max_tokens"], 160)

    def test_invalid_response_preserves_fallback(self):
        (choice, status), _, _ = self.review("not valid JSON")

        self.assertIsNone(choice)
        self.assertEqual(status, "malformed_response")


if __name__ == "__main__":
    unittest.main()
