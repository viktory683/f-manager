from unittest import TestCase

from packaging.specifiers import SpecifierSet

from f_manager_core.helpers import parse_dependencies


class TestParseDependencies(TestCase):
    dependencies = [
        "! MoreScience",
        "?ModuleInserter",
        "! Annotorio >= 0.3.0",
        "! KS_Combat >= 0.1.11",
        "? angelsindustries >= 0.4.3",
        "base >= 0.17.0",
        "(?) electricboiler",
        "? pycoalprocessing >= 1.3.4",
        "? bobwarfare >= 0.18.6",
        "(?) bobrevamp >= 1.1.5",
        "! Yuoki",
        "? NikoCharacter",
        "? genshin-impact-skin",
        "~IndustrialRevolution3 >= 3.0.8",
        "(?) Decktorio",
        "?CitiesOfEarth",
        "angelspetrochem >= 0.9.20",
        "! DeepMine",
        "?RPG",
        "? bobenemies >= 0.18.5",
        "? UltimateBelts >= 0.16.4",
        "! SchallOreConversion",
        "angelssmelting >= 0.6.17",
        "! beacon-interference",
        "? space-exploration >= 0.5.18",
        "? combat-mechanics-overhaul >= 0.6.15",
        "?inserter-throughput",
        "(?)MomoTweak",
        "! laborat >= 0.1.0",
        "(?)textplates",
        "?Kux-HandcraftGhosts",
        "?TeamCoop",
        "! modmash",
        "alien-biomes >= 0.6.5",
        "?default-wait-conditions",
        "!deadlock-beltboxes-loaders",
        "base >= 1.1.70",
        "space-exploration-graphics-2 >= 0.6.1",
        "(?) pypostprocessing",
        "(?) bobassembly",
        "(?) rso-mod >= 6.0.6",
        "! angelsrefining",
        "base >= 0.18",
        "(?) bullet-trails >= 0.4.1",
        "! pycoalprocessing",
        "simhelper >= 1.1.1",
        "IndustrialRevolution3Assets4 >= 1.0.1",
        "(?)ShinyBobGFX",
        "(?) bobclasses",
        "(?) DeadlockLargerLamp >= 1.3.1",
        "(?) qol_research",
        "! bobelectronics",
        "! angelsindustries",
        "(?) aai-industry >= 0.4.12",
        "flib",
        "! bobrevamp",
        "(?)H2O",
        "robot_attrition >= 0.5.9",
        "space-exploration-graphics >= 0.6.13",
        "AbandonedRuins >= 1.1.3",
        "Krastorio2 >= 1.0.4",
        "~ space-exploration-postprocess >= 0.6.22",
        "bobores >= 1.1.6",
        "base >= 1.1.1",
        "base >= 1.1.60",
        "Krastorio2 >= 1.2.11",
        "IndustrialRevolution3Assets2 >= 1.0.4",
        "informatron >= 0.2.1",
        "~IndustrialRevolution3 >= 3.0.1",
        "~IndustrialRevolution3 >= 3.0.7",
        "~ genshin-impact-music",
        "~ space-exploration-menu-simulations >= 0.6.7",
        "~ minime",
    ]

    def test_mandatory(self):
        mandatory, *_ = parse_dependencies(self.dependencies)

        expected_mandatory = [
            ("base", SpecifierSet(">=0.17.0")),
            ("angelspetrochem", SpecifierSet(">=0.9.20")),
            ("angelssmelting", SpecifierSet(">=0.6.17")),
            ("alien-biomes", SpecifierSet(">=0.6.5")),
            ("base", SpecifierSet(">=1.1.70")),
            ("space-exploration-graphics-2", SpecifierSet(">= 0.6.1")),
            ("base", SpecifierSet(">=0.18")),
            ("simhelper", SpecifierSet(">=1.1.1")),
            ("IndustrialRevolution3Assets4", SpecifierSet(">=1.0.1")),
            ("flib", SpecifierSet("")),
            ("robot_attrition", SpecifierSet(">=0.5.9")),
            ("space-exploration-graphics", SpecifierSet(">=0.6.13")),
            ("AbandonedRuins", SpecifierSet(">=1.1.3")),
            ("Krastorio2", SpecifierSet(">=1.0.4")),
            ("bobores", SpecifierSet(">=1.1.6")),
            ("base", SpecifierSet(">=1.1.1")),
            ("base", SpecifierSet(">=1.1.60")),
            ("Krastorio2", SpecifierSet(">=1.2.11")),
            ("IndustrialRevolution3Assets2", SpecifierSet(">=1.0.4")),
            ("informatron", SpecifierSet(">=0.2.1")),
        ]

        self.assertEqual(mandatory, expected_mandatory)

    def test_optional(self):
        _, optional, *_ = parse_dependencies(self.dependencies)

        expected_optional = [
            ("ModuleInserter", SpecifierSet("")),
            ("angelsindustries", SpecifierSet(">=0.4.3")),
            ("pycoalprocessing", SpecifierSet(">=1.3.4")),
            ("bobwarfare", SpecifierSet(">=0.18.6")),
            ("NikoCharacter", SpecifierSet("")),
            ("genshin-impact-skin", SpecifierSet("")),
            ("CitiesOfEarth", SpecifierSet("")),
            ("RPG", SpecifierSet("")),
            ("bobenemies", SpecifierSet(">=0.18.5")),
            ("UltimateBelts", SpecifierSet(">=0.16.4")),
            ("space-exploration", SpecifierSet(">=0.5.18")),
            ("combat-mechanics-overhaul", SpecifierSet(">=0.6.15")),
            ("inserter-throughput", SpecifierSet("")),
            ("Kux-HandcraftGhosts", SpecifierSet("")),
            ("TeamCoop", SpecifierSet("")),
            ("default-wait-conditions", SpecifierSet("")),
        ]

        self.assertEqual(optional, expected_optional)

    def test_hidden_optional(self):
        _, _, hidden_optional, *_ = parse_dependencies(self.dependencies)

        expected_hidden_optional = [
            ("electricboiler", SpecifierSet("")),
            ("bobrevamp", SpecifierSet(">=1.1.5")),
            ("Decktorio", SpecifierSet("")),
            ("MomoTweak", SpecifierSet("")),
            ("textplates", SpecifierSet("")),
            ("pypostprocessing", SpecifierSet("")),
            ("bobassembly", SpecifierSet("")),
            ("rso-mod", SpecifierSet(">=6.0.6")),
            ("bullet-trails", SpecifierSet(">=0.4.1")),
            ("ShinyBobGFX", SpecifierSet("")),
            ("bobclasses", SpecifierSet("")),
            ("DeadlockLargerLamp", SpecifierSet(">=1.3.1")),
            ("qol_research", SpecifierSet("")),
            ("aai-industry", SpecifierSet(">=0.4.12")),
            ("H2O", SpecifierSet("")),
        ]

        self.assertEqual(hidden_optional, expected_hidden_optional)

    def test_no_load_order(self):
        *_, no_load_order, _ = parse_dependencies(self.dependencies)

        expected_no_load_order = [
            ("IndustrialRevolution3", SpecifierSet(">=3.0.8")),
            ("space-exploration-postprocess", SpecifierSet(">=0.6.22")),
            ("IndustrialRevolution3", SpecifierSet(">=3.0.1")),
            ("IndustrialRevolution3", SpecifierSet(">=3.0.7")),
            ("genshin-impact-music", SpecifierSet("")),
            ("space-exploration-menu-simulations", SpecifierSet(">= 0.6.7")),
            ("minime", SpecifierSet("")),
        ]

        self.assertEqual(no_load_order, expected_no_load_order)

    def test_incompatible(self):
        *_, incompatible = parse_dependencies(self.dependencies)

        expected_incompatible = [
            ("MoreScience", SpecifierSet("")),
            ("Annotorio", SpecifierSet(">=0.3.0")),
            ("KS_Combat", SpecifierSet(">=0.1.11")),
            ("Yuoki", SpecifierSet("")),
            ("DeepMine", SpecifierSet("")),
            ("SchallOreConversion", SpecifierSet("")),
            ("beacon-interference", SpecifierSet("")),
            ("laborat", SpecifierSet(">=0.1.0")),
            ("modmash", SpecifierSet("")),
            ("deadlock-beltboxes-loaders", SpecifierSet("")),
            ("angelsrefining", SpecifierSet("")),
            ("pycoalprocessing", SpecifierSet("")),
            ("bobelectronics", SpecifierSet("")),
            ("angelsindustries", SpecifierSet("")),
            ("bobrevamp", SpecifierSet("")),
        ]

        self.assertEqual(incompatible, expected_incompatible)

    def test_spaces(self):
        cases = [
            "Power Armor MK3 >= 0.0.1",
            "? Flare Stack",
            "?Vehicle Wagon",
            "(?) Squeak Through >= 1.3.0",
            "!Squeak Through",
            "! Explosive Excavation",
            "~ Flow Control >= 3.0.5",
        ]
        expected = (
            [("Power Armor MK3", SpecifierSet(">=0.0.1"))],
            [
                ("Flare Stack", SpecifierSet("")),
                ("Vehicle Wagon", SpecifierSet("")),
            ],
            [("Squeak Through", SpecifierSet(">=1.3.0"))],
            [("Flow Control", SpecifierSet(">=3.0.5"))],
            [
                ("Squeak Through", SpecifierSet("")),
                ("Explosive Excavation", SpecifierSet("")),
            ],
        )

        self.assertEqual(parse_dependencies(cases), expected)
