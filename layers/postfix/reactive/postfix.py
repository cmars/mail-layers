from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charmhelpers.fetch import apt_install
from charms.reactive import hook, when, when_not, set_state, remove_state

import pki

@hook('install')
def install_postfix():
    apt_install(['postfix'])
    set_state('postfix.available')


@hook('config-changed')
def config_postfix():
    config = hookenv.config()
    if is_configured(config):
        set_state('postfix.configured')
    else:
        remove_state('postfix.configured')
        remove_state('postfix.start')


def is_configured(config):
    return config.get('hostname') and config.get('domain')


@when('postfix.configured', 'pki.cert.issued')
def setup_postfix():
    remove_state('postfix.start')

    config = hookenv.config()
    certkey = pki.certkey()
    for filename in ('main.cf', 'master.cf'):
        render(source=filename,
            target="/etc/postfix/%s" % (filename),
            owner="root",
            perms=0o644,
            context={
                'cfg': config,
                'certkey': certkey,
            })

    if host.service_running('postfix'):
        host.service_reload('postfix')
    set_state('postfix.start')


@when('postfix.start')
@when_not('postfix.started')
def start_postfix():
    host.service_start('postfix')
    set_state('postfix.started')


@when('postfix.started')
@when_not('postfix.start')
def stop_postfix():
    host.service_stop('postfix')
    remove_state('postfix.started')

