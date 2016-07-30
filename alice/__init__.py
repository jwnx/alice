import getopt
import sys

from cli import Cli


def main():

    cli = Cli()

    options, remainder = getopt.getopt(sys.argv[1:], 'u:e:lk:d',
                         ['username=',
                          'email=',
                          'public-key=',
                          'set-limits',
                          'disable'])

    for opt, arg in options:
        if opt in ('-u', '--username'):
            cli.c.set('username', arg)
        elif opt in ('-e', '--email'):
            cli.c.set('email', arg)
        elif opt in ('-k', '--public-key'):
            cli.c.set('public_key', arg)
        elif opt == '--disable':
            cli.c.set('enabled', False)

    cli.check_user_data()

if __name__ == '__main__':
    main()
