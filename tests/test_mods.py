from unittest import TestCase

from f_manager._helpers import parse_dependency

class DependencyTest(TestCase):
    deps = [
        ['?NonWaveDefense2', "NonWaveDefense2", "optional", None, None],
        ['(?) PickerAtheneum >= 1.1.2', "PickerAtheneum",
         "optional", "min_version", "1.1.2"],
        ['(?) deadlock-beltboxes-loaders',
         "deadlock-beltboxes-loaders", "optional", None, None],
        ['!omnimatter_fluid >= 3.0.0', "omnimatter_fluid",
            "conflict", "min_version", "3.0.0"],
        ['? bobelectronics', "bobelectronics", "optional", None, None],
        ['base >= 0.18', "base", "require", "min_version", "0.18"],
        ['? Clowns-Processing', "Clowns-Processing", "optional", None, None],
        ['(?)SuperExpensiveMode', "SuperExpensiveMode", "optional", None, None],
        ['!deadlock-beltboxes-loaders',
            "deadlock-beltboxes-loaders", "conflict", None, None],
        ['? base >= 1.1.70', "base", "optional", "min_version", "1.1.70"],
        ['~IndustrialRevolution3 >= 3.0.8', "IndustrialRevolution3",
            "parent", "min_version", "3.0.8"],
        ['flib', "flib", "require", None, None],
        ['?region-cloner', "region-cloner", "optional", None, None],
        ['? angelsindustries >= 0.4.3', "angelsindustries",
            "optional", "min_version", "0.4.3"],
        ['(?) Squeak Through >= 1.3.0', "Squeak Through",
         "optional", "min_version", "1.3.0"],
        ['! beacon-interference', "beacon-interference", "conflict", None, None],
        ['?Vehicle Wagon', "Vehicle Wagon", "optional", None, None],
        ['flib > 0.9.2', "flib", "require", "from_min_version", "0.9.2"],
        ['!Squeak Through', "Squeak Through", "conflict", None, None],
        ['! traintunnels <= 0.0.11', "traintunnels",
            "conflict", "max_version", "0.0.11"],
    ]

    def test_parse_dependency_name(self):
        for dep in self.deps:
            self.assertEqual(dep[1], parse_dependency(dep[0]).get("name"))

    def test_parse_dependency_category(self):
        for dep in self.deps:
            self.assertEqual(dep[2], parse_dependency(dep[0]).get("category"))

    def test_parse_dependency_min_max_version(self):
        for dep in self.deps:
            parsed_keys = list(parse_dependency(dep[0]).keys())
            parsed_keys.remove("name")
            parsed_keys.remove("category")
            val = parsed_keys[0] if parsed_keys else None
            self.assertEqual(dep[3], val)

    def test_parse_dependency_version(self):
        for dep in self.deps:
            parsed = parse_dependency(dep[0])
            parsed_keys = list(parsed.keys())
            parsed_keys.remove("name")
            parsed_keys.remove("category")
            val = parsed.get(parsed_keys[0]) if parsed_keys else None
            self.assertEqual(dep[4], val)
