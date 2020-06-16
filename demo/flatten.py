#!/usr/bin/env python3
import sys


def flatten(arr):
    res = []
    for i in arr:
        print('i: ' + str(i))

        if(type(i) is list):
            res += flatten(i)
        else:
            res += [i]
    return res


def main(args):
    arr = [1, [2, [8, [9], 'a'], [3, [4, 5, [6], 7]]]]
    flat = flatten(arr)

    print('arr: ' + str(arr) + '\nflat: ' + str(flat))


if __name__ == "__main__":
    main(sys.argv[1:])
