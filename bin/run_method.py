import argparse

import mvz.generate_video


def main():
    parser = argparse.ArgumentParser(
        description='run a mobile video creation method')
    parser.add_argument('method', type=str, help='the method to run')
    args = parser.parse_args()
    mvz_methods = __import__('mvz.methods.%s' % args.method).methods
    getattr(mvz_methods, args.method).main()
    mvz.generate_video.main(args.method, "auto")


if __name__ == '__main__':
    main()
