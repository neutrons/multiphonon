#!/usr/bin/env python


import csv

def test():
    f = "example1"
    s = open(f, 'rb')
    dialect = csv.Sniffer().sniff(s.read(1024))
    s.seek(0)
    reader = csv.reader(s, dialect)
    for row in reader:
        print row
        continue
    return


def main():
    test()
    return


if __name__ == '__main__': main()

