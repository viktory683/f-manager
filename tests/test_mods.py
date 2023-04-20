from unittest import TestCase

from packaging.specifiers import SpecifierSet

from f_manager.helpers import parse_dependencies


class TestParseDependencies(TestCase):
    dependencies = [
        '?NonWaveDefense2',
        '(?) PickerAtheneum >= 1.1.2',
        '(?) deadlock-beltboxes-loaders',
        '!omnimatter_fluid >= 3.0.0',
        '? bobelectronics',
        'base >= 0.18',
        '? Clowns-Processing',
        '(?)SuperExpensiveMode',
        '!deadlock-beltboxes-loaders',
        '? base >= 1.1.70',
        '~IndustrialRevolution3 >= 3.0.8',
        'flib',
        '?region-cloner',
        '? angelsindustries >= 0.4.3',
        '(?) Squeak Through >= 1.3.0',
        '! beacon-interference',
        '?Vehicle Wagon',
        'flib > 0.9.2',
        '!Squeak Through',
        '! traintunnels <= 0.0.11'
    ]

    def test_mandatory(self):
        mandatory, optional, hidden_optional, no_load_order, incompatible = parse_dependencies(self.dependencies)

        expected_mandatory = [
            ('base', SpecifierSet('>=0.18')),
            ('flib', SpecifierSet('')),
            ('flib', SpecifierSet('>0.9.2'))
        ]

        self.assertEqual(mandatory, expected_mandatory)

    def test_optional(self):
        mandatory, optional, hidden_optional, no_load_order, incompatible = parse_dependencies(self.dependencies)

        expected_optional = [
            ('NonWaveDefense2', SpecifierSet('')),
            ('bobelectronics', SpecifierSet('')),
            ('Clowns-Processing', SpecifierSet('')),
            ('base', SpecifierSet('>=1.1.70')),
            ('region-cloner', SpecifierSet('')),
            ('angelsindustries', SpecifierSet('>=0.4.3')),
            ('Vehicle Wagon', SpecifierSet(''))
        ]

        self.assertEqual(optional, expected_optional)

    def test_hidden_optional(self):
        mandatory, optional, hidden_optional, no_load_order, incompatible = parse_dependencies(self.dependencies)

        expected_hidden_optional = [
            ('PickerAtheneum', '>=1.1.2'),
            ('deadlock-beltboxes-loaders', None),
            ('SuperExpensiveMode', None),
            ('Squeak Through', '>=1.3.0')
        ]

        self.assertEqual(hidden_optional, expected_hidden_optional)

    def test_no_load_order(self):
        mandatory, optional, hidden_optional, no_load_order, incompatible = parse_dependencies(self.dependencies)

        expected_no_load_order = [
            ('IndustrialRevolution3', '>=3.0.8')
        ]

        self.assertEqual(no_load_order, expected_no_load_order)

    def test_incompatible(self):
        mandatory, optional, hidden_optional, no_load_order, incompatible = parse_dependencies(self.dependencies)

        expected_incompatible = [
            ('omnimatter_fluid', '>=3.0.0'),
            ('deadlock-beltboxes-loaders', None),
            ('beacon-interference', None),
            ('Squeak Through', None),
            ('traintunnels', '<=0.0.11')
        ]

        self.assertEqual(incompatible, expected_incompatible)
