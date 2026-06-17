from django.test import TestCase

from core.models import Knowledge


class KnowledgeAPIActionTests(TestCase):
    def setUp(self):
        self.pricing = Knowledge.objects.create(
            abstract="Pricing proof",
            content="Use the pricing proof point.",
        )
        self.retention = Knowledge.objects.create(
            abstract="Retention story",
            content="A longer retention narrative.",
        )

    def test_knowledge_abstract_action_returns_id_and_abstract_only(self):
        response = self.client.get("/api/knowledge/abstract/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"id": str(self.pricing.pk), "abstract": "Pricing proof"},
                {"id": str(self.retention.pk), "abstract": "Retention story"},
            ],
        )

    def test_knowledge_abstract_action_supports_search(self):
        response = self.client.get("/api/knowledge/abstract/", {"search": "pricing"})

        self.assertEqual(
            response.json(),
            [{"id": str(self.pricing.pk), "abstract": "Pricing proof"}],
        )
