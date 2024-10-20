#!/usr/bin/env python3

import unittest
from stack_machine import *
from interpreter import *
import subprocess
import io


def run(code, input_string=''):
    ist = io.StringIO(input_string)
    ost = io.StringIO()
    print()
    print(code)
    dp, data, step = brainfuck(code, ist, ost)
    print(f'Execution successfully finished in {step} steps.')
    print(f'data: {data}')
    print(f'out : {ost.getvalue()}')
    print(f'dp  : {dp}')
    return ost.getvalue(), dp, data


class TestBF(unittest.TestCase):
    def test_00_move_value1(self):
        code = 'move value1\n'
        code += '+++++\n'
        code += multi_dst_add([1])
        out, dp, data = run(code)
        self.assertEqual([0, 5], data)

    def test_01_move_value2(self):
        code = 'move value2\n'
        code += '+++++\n'
        code += multi_dst_add([2])
        out, dp, data = run(code)
        self.assertEqual([0, 0, 5], data)

    def test_02_move_value3(self):
        code = 'move value3\n'
        code += '+++++\n'
        code += multi_dst_add([1, 2])
        out, dp, data = run(code)
        self.assertEqual([0, 5, 5], data)

    def test_03_sm_load_constant(self):
        sm = StackMachine()
        code = 'sm lc\n'
        code += sm.load_constant(ord('@'))
        code += sm.put_character()
        out, dp, data = run(code)
        self.assertEqual([ord('@'), 0], data)
        self.assertEqual('@', out)

    def test_04_sm_move_variable1(self):
        sm = StackMachine()
        code = 'sm move_variable1\n'
        code += sm.load_constant(ord('@'))
        code += sm.move(0)
        out, dp, data = run(code)
        self.assertEqual([0, ord('@'), 0], data)
        self.assertEqual(dp, 2)

    def test_05_sm_move_variable2(self):
        sm = StackMachine()
        code = 'sm_move_variable2\n'
        code += sm.load_constant(ord('@'))
        for _ in range(10):
            code += sm.load_constant(0)
        code += sm.move(0)
        out, dp, data = run(code)
        self.assertEqual([0] * 11 + [ord('@'), 0], data)
        self.assertEqual(dp, 12)

    def test_06_sm_copy1(self):
        sm = StackMachine()
        code = 'sm copy1\n'
        code += sm.load_constant(ord('@'))
        code += sm.copy(0)
        out, dp, data = run(code)
        self.assertEqual([ord('@'), ord('@'), 0], data)
        self.assertEqual(dp, 2)

    def test_07_sm_add(self):
        sm = StackMachine()
        code = 'sm add\n'
        code += sm.load_constant(2)
        code += sm.load_constant(1)
        code += sm.add()
        out, dp, data = run(code)
        self.assertEqual([3, 0, 0], data)
        self.assertEqual(1, dp)

    def test_08_sm_sub(self):
        sm = StackMachine()
        code = 'sm sub\n'
        code += sm.load_constant(2)
        code += sm.load_constant(1)
        code += sm.subtract()
        out, dp, data = run(code)
        self.assertEqual([1, 0, 0], data)
        self.assertEqual(1, dp)

    def test_09_sm_addr1(self):
        sm = StackMachine()
        code = 'sm addr 1\n'
        code += sm.load_constant(2)
        code += sm.load_constant(1)
        code += sm.non_destructive_add(0, 1)
        out, dp, data = run(code)
        self.assertEqual([2, 1, 3, 0, 0], data)
        self.assertEqual(3, dp)

    def test_10_sm_addr2(self):
        sm = StackMachine()
        code = 'sm addr 2\n'
        code += sm.load_constant(2)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.load_constant(1)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.non_destructive_add(0, 3)
        out, dp, data = run(code)
        self.assertEqual([2, 0, 0, 1, 0, 0, 3, 0, 0], data)
        self.assertEqual(7, dp)

    def test_11_sm_subr1(self):
        sm = StackMachine()
        code = 'sm subr 1\n'
        code += sm.load_constant(1)
        code += sm.load_constant(2)
        code += sm.non_destructive_subtract(1, 0)
        out, dp, data = run(code)
        self.assertEqual([1, 2, 1, 0, 0], data)
        self.assertEqual(3, dp)

    def test_12_sm_subr2(self):
        sm = StackMachine()
        code = 'sm subr 2\n'
        code += sm.load_constant(1)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.load_constant(2)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.non_destructive_subtract(3, 0)
        out, dp, data = run(code)
        self.assertEqual([1, 0, 0, 2, 0, 0, 1, 0, 0], data)
        self.assertEqual(7, dp)

    def test_13_sm_fibonacci(self):
        sm = StackMachine()
        code = 'sm fibonacci\n'
        code += sm.load_constant(1)
        code += sm.load_constant(1)
        for i in range(6):
            code += sm.copy(0 + i)
            code += sm.load_constant(ord('0'))
            code += sm.add()
            code += sm.put_character()
            code += sm.load_constant(ord('0'))
            code += sm.subtract()
            code += sm.copy(1 + i)
            code += sm.add()
        out, dp, data = run(code)
        self.assertEqual('112358', out)
        self.assertEqual([1, 1, 2, 3, 5, 8, 13, 21, 0, 0], data)
        self.assertEqual(8, dp)

    def test_14_sm_multiply1(self):
        sm = StackMachine()
        code = 'sm mul1\n'
        code += sm.load_constant(3)
        code += sm.load_constant(2)
        code += sm.multiply()
        out, dp, data = run(code)
        self.assertEqual([6, 0, 0, 0], data)
        self.assertEqual(1, dp)

    def test_15_sm_multiply2(self):
        sm = StackMachine()
        code = 'sm mul2\n'
        code += sm.load_constant(1)
        code += sm.load_constant(2)
        code += sm.load_constant(3)
        code += sm.multiply()
        code += sm.multiply()
        out, dp, data = run(code)
        self.assertEqual([6, 0, 0, 0, 0], data)
        self.assertEqual(1, dp)

    def test_16_sm_non_destructive_multiply1(self):
        sm = StackMachine()
        code = 'sm mulnd1\n'
        code += sm.load_constant(2)
        code += sm.load_constant(3)
        code += sm.non_destructive_multiply(0, 1)
        out, dp, data = run(code)
        self.assertEqual([2, 3, 6, 0, 0, 0], data)
        self.assertEqual(3, dp)

    def test_17_sm_non_destructive_multiply2(self):
        sm = StackMachine()
        code = 'sm mulnd2\n'
        code += sm.load_constant(5)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.load_constant(51)
        code += sm.load_constant(0)
        code += sm.load_constant(0)
        code += sm.non_destructive_multiply(0, 3)
        out, dp, data = run(code)
        self.assertEqual([5, 0, 0, 51, 0, 0, 255, 0, 0, 0], data)
        self.assertEqual(7, dp)

    def test_18_sm_bool1(self):
        sm = StackMachine()
        code = 'sm bool1\n'
        code += sm.load_constant(10)
        code += sm.boolean()
        out, dp, data = run(code)
        self.assertEqual([1, 0], data)
        self.assertEqual(1, dp)

    def test_19_sm_bool2(self):
        sm = StackMachine()
        code = 'sm bool2\n'
        code += sm.load_constant(0)
        code += sm.boolean()
        out, dp, data = run(code)
        self.assertEqual([0, 0], data)
        self.assertEqual(1, dp)

    def test_20_sm_bool1(self):
        sm = StackMachine()
        code = 'sm boolnd1\n'
        code += sm.load_constant(10)
        code += sm.load_constant(1)
        code += sm.load_constant(1)
        code += sm.load_constant(1)
        code += sm.non_destructive_boolean(0)
        out, dp, data = run(code)
        self.assertEqual([10, 1, 1, 1, 1, 0], data)
        self.assertEqual(5, dp)

    def test_21_sm_bool2(self):
        sm = StackMachine()
        code = 'sm boolnd2\n'
        code += sm.load_constant(0)
        code += sm.load_constant(1)
        code += sm.load_constant(1)
        code += sm.load_constant(1)
        code += sm.non_destructive_boolean(0)
        out, dp, data = run(code)
        self.assertEqual([0, 1, 1, 1, 0, 0], data)
        self.assertEqual(5, dp)

    def test_22_sm_while1(self):
        sm = StackMachine()
        code = 'sm while1\n'
        code += sm.load_constant(10)
        code += sm.beginwhile()
        code += sm.load_constant(1)
        code += sm.subtract()
        code += sm.endwhile()
        out, dp, data = run(code)
        self.assertEqual([0, 0, 0], data)
        self.assertEqual(1, dp)

    def test_23_sm_while2(self):
        sm = StackMachine()
        code = 'sm while2\n'
        code += sm.load_constant(100)
        code += sm.beginwhile()
        code += sm.load_constant(1)
        code += sm.subtract()
        code += sm.load_constant(100)
        code += sm.beginwhile()
        code += sm.load_constant(1)
        code += sm.subtract()
        code += sm.endwhile()
        code += sm.endwhile()
        self.assertEqual(sm.controlstack, [])
        out, dp, data = run(code)
        self.assertEqual([0, 0, 0, 0], data)
        self.assertEqual(1, dp)


if __name__ == '__main__':
    unittest.main()
