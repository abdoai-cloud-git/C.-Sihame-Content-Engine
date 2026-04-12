import unittest

from app.models.schemas import VoiceRoute
from app.services.context_builder import DynamicContextBuilder


class DynamicContextBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = DynamicContextBuilder()

    def test_reflection_routes_to_2023_voice(self) -> None:
        assembled = self.builder.build_payload("Talk about inner fear.", "Reflection", "telegram")
        self.assertEqual(assembled.routing_metadata.voice_route, VoiceRoute.SOUL_2023)
        self.assertIn("STYLE_BIBLE_MASTER.md", assembled.routing_metadata.injected_files)
        self.assertIn("PRIMARY_GOLD_EXAMPLES.md", assembled.routing_metadata.example_files)

    def test_guided_practice_routes_to_methodology(self) -> None:
        assembled = self.builder.build_payload("Guide a grounding exercise.", "Guided Practice", "telegram")
        self.assertEqual(assembled.routing_metadata.voice_route, VoiceRoute.METHODOLOGY)
        self.assertNotIn("STYLE_BIBLE_MASTER.md", assembled.routing_metadata.injected_files)
        self.assertIn("SECONDARY_EXAMPLE_FRAGMENTS.md", assembled.routing_metadata.example_files)

    def test_promo_routes_to_hybrid(self) -> None:
        assembled = self.builder.build_payload("Invite them to a PEAT program.", "Promo", "instagram")
        self.assertEqual(assembled.routing_metadata.voice_route, VoiceRoute.HYBRID)
        self.assertIn("VOICE_ROUTING_RULES.md", assembled.routing_metadata.injected_files)
        self.assertIn("PRIMARY_GOLD_EXAMPLES.md", assembled.routing_metadata.example_files)

    def test_monthly_intention_routes_to_ritual(self) -> None:
        assembled = self.builder.build_payload("Monthly intention for April.", "Monthly Intention", "telegram")
        self.assertEqual(assembled.routing_metadata.voice_route, VoiceRoute.RITUAL)
        self.assertIn("RITUAL_TEMPLATES_2023.md", assembled.routing_metadata.injected_files)
        self.assertIn("RITUAL_TEMPLATES_2023.md", assembled.routing_metadata.example_files)

    def test_rejection_feedback_is_injected_for_regeneration(self) -> None:
        assembled = self.builder.build_payload(
            "Talk about inner fear.",
            "Reflection",
            "telegram",
            rejection_feedback="Too generic and too fast.",
        )
        self.assertIn("REGENERATION FEEDBACK", assembled.prompt)
        self.assertIn("Too generic and too fast.", assembled.prompt)
