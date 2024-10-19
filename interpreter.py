#!/usr/bin/env python3

import sys

def brainfuck(prog, ist=sys.stdin, ost=sys.stdout):
    ip = 0
    dp = 0
    maxdp = 0
    data = [0] * (1 << 16)
    while ip < len(prog):
        if prog[ip] == '>':
            dp += 1
            maxdp = max(maxdp, dp)
        elif prog[ip] == '<':
            dp -= 1
        elif prog[ip] == '+':
            data[dp] = (data[dp] + 1) & 0xFF
        elif prog[ip] == '-':
            data[dp] = (data[dp] - 1) & 0xFF
        elif prog[ip] == '.':
            print(chr(data[dp]), end='', file=ost)
        elif prog[ip] == ',':
            data[dp] = ord(ist.read(1))
        elif prog[ip] == '[':
            if data[dp] == 0:
                cnt = 1
                while cnt:
                    ip += 1
                    if prog[ip] == '[':
                        cnt += 1
                        maxdp = max(maxdp, dp)
                    elif prog[ip] == ']':
                        cnt -= 1
        elif prog[ip] == ']':
            if data[dp] != 0:
                cnt = 1
                while cnt:
                    ip -= 1
                    if prog[ip] == ']':
                        cnt += 1
                        maxdp = max(maxdp, dp)
                    elif prog[ip] == '[':
                        cnt -= 1
        ip += 1
    return dp, data[0:maxdp+1]
