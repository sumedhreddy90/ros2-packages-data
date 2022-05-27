#!/usr/bin/env python3
import argparse

from ros_data.packages import update_packages


if __name__ == '__main__':
    modules = {
        'packages': update_packages
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('modules', metavar='module', choices=sorted(list(modules.keys()) + ['all']), nargs='*',
                        default='all')
    args = parser.parse_args()
    if 'all' in args.modules:
        args.modules = list(modules.keys())

    for key in args.modules:
        modules[key]()