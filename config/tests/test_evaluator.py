import unittest
from config.ast import *
from config.evaluator import Evaluator


class TestEvaluator(unittest.TestCase):
    def test_basic_evaluation(self):
        root = Struct({
            'count': Number(42),
            'pi': Number(3.14),
            'active': String('true')
        })

        evaluator = Evaluator()
        result = evaluator.evaluate({'consts': [], 'root': root})

        self.assertEqual(result, {
            'count': 42.0,
            'pi': 3.14,
            'active': 'true'
        })

    def test_constants_and_expressions(self):
        consts = [
            ConstDeclaration('TWO', Number(2)),
            ConstDeclaration('HALF', Number(0.5))
        ]

        root = Struct({
            'double': ConstExpression(['TWO', 'TWO', '*']),
            'sqrt': ConstExpression(['TWO', 'sqrt']),
            'fraction': ConstExpression(['HALF', '2', '*'])
        })

        evaluator = Evaluator()
        result = evaluator.evaluate({'consts': consts, 'root': root})

        self.assertAlmostEqual(result['double'], 4.0)
        self.assertAlmostEqual(result['sqrt'], 1.41421356237, places=5)
        self.assertAlmostEqual(result['fraction'], 1.0, places=5)

    def test_unicode_and_special_chars(self):
        """Проверка поддержки Unicode и спецсимволов"""
        root = Struct({
            'name': String('Элиандра'),
            'description': String('Сила — в знании\\n"Мудрость"'),
            'physics': String('E = mc²')
        })

        evaluator = Evaluator()
        result = evaluator.evaluate({'consts': [], 'root': root})

        self.assertEqual(result['name'], 'Элиандра')
        self.assertIn('Сила — в знании', result['description'])
        self.assertIn('mc²', result['physics'])

    def test_complex_expressions_from_examples(self):
        """Проверка выражений из реальных примеров"""
        consts = [
            ConstDeclaration('BaseInt', Number(20)),
            ConstDeclaration('Pi', Number(3.1415926535)),
            ConstDeclaration('MinPort', Number(8000)),
            ConstDeclaration('MaxPort', Number(9000)),
        ]

        root = Struct({
            'SpellPower': ConstExpression(['BaseInt', '1.5', '*']),
            'Sqrt2': ConstExpression(['2', 'sqrt']),
        })

        evaluator = Evaluator()
        result = evaluator.evaluate({'consts': consts, 'root': root})

        # Проверка вычислений из character.conf
        self.assertAlmostEqual(result['SpellPower'], 30.0, places=5)

        # Проверка вычислений из physics.conf
        self.assertAlmostEqual(result['Sqrt2'], 1.41421356237, places=10)

    def test_nested_structs(self):
        inner = Struct({
            'port': Number(8080),
            'host': String('localhost')
        })

        root = Struct({
            'database': inner,
            'debug': ConstExpression(['1', '1', '+'])
        })

        evaluator = Evaluator()
        result = evaluator.evaluate({'consts': [], 'root': root})

        self.assertEqual(result, {
            'database': {
                'port': 8080.0,
                'host': 'localhost'
            },
            'debug': 2.0
        })

    def test_division_by_zero(self):
        evaluator = Evaluator()
        root = Struct({
            'invalid': ConstExpression(['10', '0', '/'])
        })

        with self.assertRaises(ZeroDivisionError):
            evaluator.evaluate({'consts': [], 'root': root})

    def test_unknown_constant(self):
        evaluator = Evaluator()
        root = Struct({
            'invalid': ConstExpression(['UNKNOWN'])
        })

        with self.assertRaises(NameError):
            evaluator.evaluate({'consts': [], 'root': root})


if __name__ == '__main__':
    unittest.main()