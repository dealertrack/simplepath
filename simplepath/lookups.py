# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
from decimal import Decimal


class BaseLookup(object):
    def config(self, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        self.expression = kwargs.pop('expression')
        self.config(*args, **kwargs)
        return self

    def repr(self):
        return ''

    def call_expression(self, expression, data, extra):
        return expression(
            data,
            super_root=extra.get('super_root'),
            # cant use global lut since state can leak between calls
            lut={},
            context=extra.get('context'),
        )

    def __call__(self, node, extra=None):
        """
        Returns the desired value according to the below logic
        and using the value in the current node.

        Note:
            When overriding this method, make sure to not modify
            any attribute in self unless unexpected behavior will result.
            In other words, attributes of self must be considered
            immutable.
        """
        raise NotImplementedError

    def __repr__(self):
        return (
            '<{} {}>'.format(
                self.__class__.__name__,
                self.repr(),
            )
        )


class KeyLookup(BaseLookup):
    def config(self, key):
        self.key = key

    def __call__(self, node, extra=None):
        if isinstance(node, (list, tuple)):
            return node[int(self.key)]
        else:
            return node[self.key]

    def repr(self):
        return 'key="{}"'.format(self.key)


class FindInListLookup(BaseLookup):
    def config(self, **conditions):
        self.conditions = conditions

    def __call__(self, nodes, extra=None):
        for node in nodes:
            present = {k: node.get(k) for k in self.conditions}
            if present == self.conditions:
                return node
        raise ValueError('Not found any node matching all conditions')

    def repr(self):
        return ', '.join(
            '{}="{}"'.format(k, v)
            for k, v in self.conditions.items()
        )


class LUTLookup(KeyLookup):
    def __call__(self, node, extra=None):
        return extra['lut'][self.key]


class AsTypeLookup(BaseLookup):
    """
    Convert the type of the node to the desired type.
    Example: To return the integer value of the current node, do
    <as_type:int>
    """
    TYPES = {
        "int": int,
        "float": float,
        "decimal": Decimal,
        "bool": bool
    }

    def config(self, type_name):
        if type_name not in self.TYPES:
            raise ValueError('Unsupported type {}'.format(type_name))
        self.type = self.TYPES[type_name]

    def __call__(self, node, extra=None):
        return self.type(node)


class ArithmeticLookup(BaseLookup):
    """
    Perform an arithmetic operation on two operands and return the value.
    <arith:operator_str,operand,reverse>
    Example: To return the quotient of 12 with the current node do
    <arith://,12,reverse=True>

    Note that / will use true division while // will use floordiv.
    """
    OPERATORS = {
        '/': operator.truediv,
        '//': operator.floordiv,
        '*': operator.mul,
        '+': operator.add,
        '-': operator.sub,
        '%': operator.mod,
        '^': operator.pow
    }

    def config(self, oper_name, operand, reverse=False):
        """
        Args:
            oper_name (str): the name of the operator to use (ex: +, %)
            operand (str): the value of the right operand for the
                           operation
            reverse (bool): whether the operation should be reversed;
                            Example: for subtraction, operand - node
        """
        if oper_name not in self.OPERATORS.keys():
            raise ValueError('Unsupported operator {}'.format(oper_name))

        self.operator = self.OPERATORS[oper_name]
        self.reverse = reverse
        self.operand = operand

    def __call__(self, node, extra=None):
        if self.reverse:
            return self.operator(type(node)(self.operand), node)
        return self.operator(node, type(node)(self.operand))
