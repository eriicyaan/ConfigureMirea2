# config_lang/evaluator.py

import math
from config.ast import Number, String, Struct, Identifier, ConstExpression


class Evaluator:
    def __init__(self):
        self.constants = {}

    def evaluate(self, ast):
        # Вычисляем константы
        for decl in ast['consts']:
            value = self._evaluate_node(decl.value_node)
            if not isinstance(value, (int, float, str)):
                raise TypeError(f"Constant '{decl.name}' must be a number or string")
            self.constants[decl.name] = value

        # Вычисляем корневую структуру
        return self._evaluate_struct(ast['root'])

    def _evaluate_node(self, node):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, ConstExpression):
            return self._evaluate_expression(node.tokens)
        elif isinstance(node, Struct):
            return self._evaluate_struct(node)
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Identifier):
            if node.name not in self.constants:
                raise NameError(f"Undefined constant '{node.name}'")
            return self.constants[node.name]
        else:
            raise TypeError(f"Unknown node type: {type(node)}")

    def _evaluate_expression(self, tokens):
        stack = []
        for token in tokens:
            if self._is_number(token):
                stack.append(float(token))
            elif token in self.constants:
                value = self.constants[token]
                if not isinstance(value, (int, float)):
                    raise TypeError(f"Constant '{token}' used in expression must be a number")
                stack.append(value)
            elif token == '+':
                self._apply_binary_op(stack, lambda a, b: a + b, token)
            elif token == '-':
                self._apply_binary_op(stack, lambda a, b: a - b, token)
            elif token == '*':
                self._apply_binary_op(stack, lambda a, b: a * b, token)
            elif token == '/':
                self._apply_binary_op(stack, lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(
                    ZeroDivisionError("Division by zero")), token)
            elif token == 'mod':
                self._apply_binary_op(stack, lambda a, b: a % b, token)
            elif token == 'sqrt':
                self._apply_unary_op(stack, lambda a: math.sqrt(a) if a >= 0 else (_ for _ in ()).throw(
                    ValueError("Negative number in sqrt")), token)
            else:
                raise NameError(f"Unknown token in expression: '{token}'")

        if len(stack) != 1:
            raise ValueError(f"Invalid expression: expected 1 value on stack, got {len(stack)}")
        return stack[0]

    def _apply_binary_op(self, stack, op, token):
        if len(stack) < 2:
            raise ValueError(f"Not enough operands for operator '{token}'")
        b = stack.pop()
        a = stack.pop()
        try:
            stack.append(op(a, b))
        except ZeroDivisionError:
            raise ZeroDivisionError(f"Division by zero in expression") from None
        except Exception as e:
            raise ValueError(f"Error in operation '{token}': {str(e)}") from e

    def _apply_unary_op(self, stack, op, token):
        if len(stack) < 1:
            raise ValueError(f"Not enough operands for operator '{token}'")
        a = stack.pop()
        try:
            stack.append(op(a))
        except Exception as e:
            raise ValueError(f"Error in operation '{token}': {str(e)}") from e

    def _evaluate_struct(self, struct_node):
        result = {}
        for name, value_node in struct_node.fields.items():
            result[name] = self._evaluate_node(value_node)
        return result

    @staticmethod
    def _is_number(token):
        try:
            float(token)
            return True
        except ValueError:
            return False