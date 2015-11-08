import os
import shutil
import subprocess

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charmhelpers.fetch import apt_install
from charms.reactive import hook, when, when_not, is_state, set_state, remove_state
from charms.reactive.bus import get_states

import pki


@hook('install')
def install_dovecot():
    apt_install(['dovecot-common', 'dovecot-imapd'])


@hook('config-changed')
def config_dovecot():
    set_state('dovecot.configured')


@when('dovecot.configured', 'pki.cert.issued')
def setup_dovecot():
    config = hookenv.config()
    certkey = pki.certkey()
    for filename in ('10-master.conf', '10-ssl.conf'):
        render(source=filename,
            target="/etc/dovecot/conf.d/%s" % (filename),
            owner="root",
            perms=0o644,
            context={
                'cfg': config,
                'certkey': certkey,
            })
    if host.service_running('dovecot'):
        host.service_reload('dovecot')
    set_state('dovecot.start')
 

@when('dovecot.start')
@when_not('dovecot.started')
def start_dovecot():
    host.service_start('dovecot')
    set_state('dovecot.started')


@when('dovecot.started')
@when_not('dovecot.start')
def stop_dovecot():
    host.service_stop('dovecot')
    remove_state('dovecot.started')

