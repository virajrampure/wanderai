import unittest
from app.rag import KnowledgeBase
from app.planner import plan_trip, pick_tier
from app.chat import chat

kb = KnowledgeBase()


class CoreTests(unittest.TestCase):
    def test_search_filters_destination(self):
        hits = kb.search("beach water sports", dest="Goa", kind="attraction", k=3)
        self.assertTrue(all(d["dest"] == "Goa" for _, d in hits))
        self.assertIn("Beach", hits[0][1]["item"]["name"])

    def test_plan_respects_day_hours(self):
        p = plan_trip(kb, "Jaipur", 3, 30000, 2, ["history", "shopping"], use_weather=False)
        self.assertEqual(len(p["itinerary"]), 3)
        self.assertTrue(all(d["hours"] <= 7.0 for d in p["itinerary"]))
        names = [s["name"] for d in p["itinerary"] for s in d["stops"]]
        self.assertEqual(len(names), len(set(names)))  # no duplicates
        self.assertIn("Amber Fort", names)

    def test_budget_math(self):
        p = plan_trip(kb, "Goa", 2, 10000, 2, ["beach"], use_weather=False)
        b = p["budget"]
        self.assertEqual(b["estimated_total"], b["entry_fees"] + b["stay_food_transport"])
        self.assertEqual(b["within_budget"], b["estimated_total"] <= 10000)

    def test_tier(self):
        self.assertEqual(pick_tier(3000, 3, 1)[0], "budget")
        self.assertEqual(pick_tier(60000, 3, 2)[0], "comfort")

    def test_unknown_destination(self):
        with self.assertRaises(ValueError):
            plan_trip(kb, "Atlantis", 2, 5000, use_weather=False)

    def test_chat_detects_destination(self):
        r = chat(kb, "What is the best time to visit Goa?")
        self.assertEqual(r["destination"], "Goa")
        self.assertTrue(r["sources"])


if __name__ == "__main__":
    unittest.main()
