#!/usr/bin/env python3

def sanitize(num):
    if num < 0:
        return f'neg{-num}'
    else:
        return f'{num}'

def mvp(num):
    if num < 0:
        return '<' * -num
    else:
        return '>' * num

def inc(num):
    if num < 0:
        return '-' * -num
    else:
        return '+' * num

def multi_dst_add(dsts):
    '''Distribute data[dp] to data[dp + i] for i in DSTS.
    The data pointer returns where before execution.
    '''
    assert dsts
    assert 0 not in dsts
    data = sorted(set(dsts))
    ascending = [data[i + 1] - data[i] for i in range(len(data) - 1)]
    begin = data[0]
    code = ''
    code += f'[-{mvp(begin)}+'
    ret = begin
    for diff in ascending:
        ret += diff
        code += f'{mvp(diff)}+'
    code += f'{mvp(-ret)}]'
    return code

def multi_dst_subtract(dsts):
    '''Same as multi_dst_add but it subtract.
    '''
    assert dsts
    assert 0 not in dsts
    data = sorted(set(dsts))
    ascending = [data[i + 1] - data[i] for i in range(len(data) - 1)]
    begin = data[0]
    code = ''
    code += f'[-{mvp(begin)}-'
    ret = begin
    for diff in ascending:
        ret += diff
        code += f'{mvp(diff)}-'
    code += f'{mvp(-ret)}]'
    return code

class StackMachine:
    def __init__(self):
        self.dp = 0

    def load_constant(self, value):
        '''Load constant and push to the stack top.
        data[dp] = value; dp++
        '''
        self.dp += 1
        return f'lv {sanitize(value)}:[-]{inc(value)}>\n'

    def put_character(self):
        '''Put the stack top byte.
        putc(data[dp - 1])
        '''
        return f'putc:<.>\n'

    def get_character(self):
        '''Get byte and push to the stack top.
        data[dp] = getc(); dp++
        '''
        self.dp += 1
        return 'getc:,>\n'

    def move(self, pos):
        '''Move a byte of POS and push to the stack top.
        data[dp] = data[pos]; data[pos] = 0; dp++
        '''
        assert 0 <= pos < self.dp
        rpos = pos - self.dp
        code = f'mv {sanitize(pos)}:'
        code += '[-]'
        code += mvp(rpos)
        code += multi_dst_add([-rpos])
        code += mvp(-rpos)
        code += '>'
        self.dp += 1
        return code + '\n'

    def copy(self, pos):
        '''Copy a byte of POS and push to the stack top.
        data[dp] = data[pos]; data[dp + 1] = 0; dp++
        '''
        assert 0 <= pos < self.dp
        rpos = pos - self.dp
        code = f'cp {sanitize(rpos)}:'
        code += '[-]>[-]<'
        code += mvp(rpos)
        code += multi_dst_add([-rpos, -rpos + 1])
        code += mvp(-rpos + 1)
        code += multi_dst_add([rpos - 1])
        self.dp += 1
        return code + '\n'

    def add(self):
        '''Add and pop two stack top bytes, and push the result to the stack top.
        data[dp - 2] = data[dp - 2] + data[dp - 1]; data[dp - 1] = 0; dp--
        '''
        assert 1 < self.dp
        code = 'add:'
        code += '<' + multi_dst_add([-1])
        self.dp -= 1
        return code + '\n'

    def subtract(self):
        '''Subtract the stack top byte from the stack second byte and pop both, push the result to the stack top.
        data[dp - 2] = data[dp - 2] - data[dp - 1]; data[dp - 1] = 0; dp--
        '''
        assert 1 < self.dp
        code = 'sub:'
        code += '<' + multi_dst_subtract([-1])
        self.dp -= 1
        return code + '\n'

    def multiply(self):
        '''Multiply and pop two stack top bytes, and push the result to the stack top.
        data[dp - 2] = data[dp - 2] * data[dp - 1]; data[dp] = 0; data[dp - 1] = 0; dp--
        '''
        assert 1 < self.dp
        code = 'mul:'
        code += '[-]>[-]<<'
        code += '[-<'
        code += multi_dst_add([2, 3])
        code += '>>>'
        code += multi_dst_add([-3])
        code += '<<]'
        code += '<[-]>>'
        code += multi_dst_add([-2])
        code += '<'
        self.dp -= 1
        return code + '\n'

    def non_destructive_multiply(self, pos1, pos2):
        '''Multiply bytes of POS1 and POS2, push to the stack top.
        data[dp] = data[pos1] + data[pos2]; data[dp + 1] = 0; data[dp + 2] = 0; dp++
        '''
        assert pos1 != pos2
        assert 0 <= pos1
        assert 0 <= pos2
        rpos1 = pos1 - self.dp
        rpos2 = pos2 - self.dp
        code = f'mulnd {pos1} {pos2}:'
        code += '[-]>[-]>[-]>[-]<<<'
        # copy from pos1 to dp
        code += mvp(rpos1)
        code += multi_dst_add([-rpos1, -rpos1 + 1])
        code += mvp(-rpos1 + 1)
        code += multi_dst_add([rpos1 - 1])
        # copy from pos2 to dp + 1
        code += mvp(rpos2 - 1)
        code += multi_dst_add([-rpos2 + 1, -rpos2 + 2])
        code += mvp(-rpos2 + 2)
        code += multi_dst_add([rpos2 - 2])
        # multiply stacktop
        code += '<'
        code += '[-<'
        code += multi_dst_add([2, 3])
        code += '>>>'
        code += multi_dst_add([-3])
        code += '<<]'
        code += '<[-]>>'
        code += multi_dst_add([-2])
        code += '<'
        self.dp += 1
        return code

    def non_destructive_add(self, pos1, pos2):
        '''Add bytes of POS1 and POS2, push to the stack top.
        data[dp] = data[pos1] + data[pos2]; data[dp + 1] = 0; data[dp + 2] = 0; dp++
        '''
        assert pos1 != pos2
        assert 0 <= pos1
        assert 0 <= pos2
        rpos1 = pos1 - self.dp
        rpos2 = pos2 - self.dp
        code = f'addnd {sanitize(rpos1)} {sanitize(rpos2)}:'
        code += '[-]>[-]>[-]<<'
        code += mvp(rpos1)
        code += multi_dst_add([-rpos1, -rpos1 + 1])
        code += mvp(-rpos1 + 1)
        code += multi_dst_add([rpos1 - 1])
        code += mvp(rpos2 - 1)
        code += multi_dst_add([-rpos2 + 1, -rpos2 + 2])
        code += mvp(-rpos2 + 2)
        code += multi_dst_add([rpos2 - 2])
        code += '<'
        code += multi_dst_add([-1])
        self.dp += 1
        return code

    def non_destructive_subtract(self, pos1, pos2):
        '''Subtract a byte of POS2 from POS1, push to the stack top.
        data[dp] = data[pos1] - data[pos2]; data[dp + 1] = 0; data[dp + 2] = 0; dp++
        '''
        assert pos1 != pos2
        assert 0 <= pos1
        assert 0 <= pos2
        rpos1 = pos1 - self.dp
        rpos2 = pos2 - self.dp
        code = f'subnd {sanitize(rpos1)} {sanitize(rpos2)}:'
        code += '[-]>[-]>[-]<<'
        code += mvp(rpos1)
        code += multi_dst_add([-rpos1, -rpos1 + 1])
        code += mvp(-rpos1 + 1)
        code += multi_dst_add([rpos1 - 1])
        code += mvp(rpos2 - 1)
        code += multi_dst_add([-rpos2 + 1, -rpos2 + 2])
        code += mvp(-rpos2 + 2)
        code += multi_dst_add([rpos2 - 2])
        code += '<'
        code += multi_dst_subtract([-1])
        self.dp += 1
        return code
