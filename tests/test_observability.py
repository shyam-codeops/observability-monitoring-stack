"""
Automated unit tests validating Prometheus, Alertmanager, and Grafana configurations.
"""

import os
import json
import re
import unittest


class TestObservabilityStack(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def read_file(self, rel_path: str) -> str:
        full_path = os.path.join(self.repo_root, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_prometheus_config(self):
        content = self.read_file("prometheus/prometheus.yml")
        self.assertIn("scrape_interval: 15s", content)
        self.assertIn("alertmanager:9093", content)
        self.assertIn("rules/*.yaml", content)

    def test_alert_rules_definitions(self):
        content = self.read_file("prometheus/rules/alerts.yaml")
        self.assertIn("alert: NodeHighCpuUsage", content)
        self.assertIn("alert: NodeHighMemoryUsage", content)
        self.assertIn("alert: ContainerCrashLoopBackOff", content)
        self.assertIn("alert: HighHttpErrorRate5xx", content)
        self.assertIn("alert: SloErrorBudgetRapidBurn", content)
        # Check runbook URLs are defined for SRE troubleshooting
        self.assertIn("runbook_url:", content)

    def test_alertmanager_routing(self):
        content = self.read_file("alertmanager/alertmanager.yml")
        self.assertIn("receiver: \"slack-notifications\"", content)
        self.assertIn("inhibit_rules:", content)
        self.assertIn("pagerduty-sre", content)

    def test_grafana_dashboard_valid_json(self):
        content = self.read_file("grafana/dashboards/kubernetes-cluster-overview.json")
        data = json.loads(content)
        self.assertEqual(data["uid"], "k8s-slo-overview")
        self.assertGreater(len(data["panels"]), 0)
        panel_titles = [p.get("title") for p in data["panels"]]
        self.assertIn("CPU Utilization (%)", panel_titles)
        self.assertIn("Memory Utilization (%)", panel_titles)

    def test_docker_compose_services(self):
        content = self.read_file("docker-compose.yml")
        self.assertIn("prometheus:", content)
        self.assertIn("grafana:", content)
        self.assertIn("alertmanager:", content)
        self.assertIn("loki:", content)
        self.assertIn("tempo:", content)


if __name__ == "__main__":
    unittest.main()
