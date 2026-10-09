"""Offline public-demo tests. No Qloo, Ollama or cloud calls."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import app
from public_guard import DemoBudget


class GuardTests(unittest.TestCase):
    def test_budget_hour_and_day(self):
        clock = [100000.0]
        budget = DemoBudget(hourly=1, daily=2, clock=lambda: clock[0])
        self.assertIsNone(budget.admit())
        budget.release()
        self.assertEqual(budget.admit(), "hourly_limit")
        clock[0] += 3601
        self.assertIsNone(budget.admit())
        budget.release()
        self.assertEqual(budget.admit(), "daily_limit")
        clock[0] += 86401
        self.assertIsNone(budget.admit())
        budget.release()

    def test_concurrency(self):
        budget = DemoBudget(hourly=8, daily=8, concurrent=1)
        self.assertIsNone(budget.admit())
        self.assertEqual(budget.admit(), "busy")
        budget.release()
        self.assertIsNone(budget.admit())
        budget.release()

    def test_public_startup_requires_secrets_and_remote_llm(self):
        with patch.object(app, "HOST", "0.0.0.0"), patch.object(app, "PUBLIC_DEMO", False):
            with self.assertRaises(SystemExit):
                app.validate_public_settings()
        with patch.object(app, "HOST", "0.0.0.0"), patch.object(app, "PUBLIC_DEMO", True), \
             patch.object(app, "ENV_KEY", ""):
            with self.assertRaises(SystemExit):
                app.validate_public_settings()
        with patch.object(app, "HOST", "0.0.0.0"), patch.object(app, "PUBLIC_DEMO", True), \
             patch.object(app, "ENV_KEY", "server_qloo"), \
             patch.dict("os.environ", {"ATLAS_LLM_URL": "http://127.0.0.1:11434/v1/chat/completions", "ATLAS_LLM_MODEL": "qwen", "ATLAS_LLM_API_KEY": "token"}):
            with self.assertRaises(SystemExit):
                app.validate_public_settings()
        with patch.object(app, "HOST", "0.0.0.0"), patch.object(app, "PUBLIC_DEMO", True), \
             patch.object(app, "ENV_KEY", "server_qloo"), \
             patch.dict("os.environ", {"ATLAS_LLM_URL": "https://api.example/v1/chat/completions", "ATLAS_LLM_MODEL": "model", "ATLAS_LLM_API_KEY": "token"}):
            app.validate_public_settings()


class PublicHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def _post(self, data, content_type="application/json"):
        req = urllib.request.Request(
            self.base + "/api/program", data=json.dumps(data).encode(),
            headers={"Content-Type": content_type}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as ex:
            with ex:
                return ex.code, json.load(ex)

    def test_public_ignores_browser_supplied_api_key(self):
        fields = {"artist": "Nils Frahm", "city": "Madrid", "objective": "Educational workshop", "api_key": "attacker_key"}
        with patch.object(app, "PUBLIC_DEMO", True), patch.object(app, "ENV_KEY", "server_secret"), \
             patch.object(app, "HOST", "0.0.0.0"), \
             patch.object(app, "PUBLIC_BUDGET", DemoBudget(hourly=2, daily=3)), \
             patch.object(app, "run_research", return_value={"concepts": []}) as research:
            status, body = self._post(fields)
            self.assertEqual(status, 200)
            self.assertEqual(body["concepts"], [])
            research.assert_called_once_with("server_secret", "Nils Frahm", "Madrid", "Educational workshop")
            status, _ = self._post(fields)
            self.assertEqual(status, 200)
            status, body = self._post(fields)
            self.assertEqual(status, 429)
            self.assertEqual(body["reason"], "hourly_limit")
            self.assertEqual(research.call_count, 2)

    def test_content_type_guard_before_qloo(self):
        with patch.object(app, "run_research") as research:
            status, _ = self._post({"artist":"Nils Frahm"}, "text/plain")
            self.assertEqual(status, 415)
            research.assert_not_called()


if __name__ == "__main__":
    unittest.main()
