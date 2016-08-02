# Simple revalidation service to check pull requests which a) haven't been checked
# b) were by a trusted user. This is necessary as sometimes an error will cause part of
# the validation process to not occur. For example, if we attempt to merge to prs too
# quickly, github will reject the second merge as the ref may be out of date (#63).

from threading import Timer
from pytimeparse.timeparse import timeparse

def start(bot):
    interval = timeparse(bot.config['recheck_interval'])
    start_timer(bot, interval)

def start_timer(bot, interval):
    print 'Checking all open pull requests in %d seconds' % interval
    t = Timer(interval, check_all_open_prs, (bot, interval))
    t.start()

def check_all_open_prs(bot, interval=None):
    print 'Revalidation begining on select open pull requests'
    for pr in bot.repo.iter_pulls(state='open'):
        if bot.is_trusted(pr.user):
            bot.validate(pr)
    if interval is not None: start_timer(bot, interval)
