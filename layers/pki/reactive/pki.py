import os
import shutil
import subprocess

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charmhelpers.fetch import apt_install
from charms.reactive import hook, when, when_not, is_state, set_state, remove_state
from charms.reactive.bus import get_states


@hook('install')
def install_cfssl():
    apt_install(['libltdl7'])
    for filename in ('cfssl', 'cfssljson'):
        install_binary(filename)
    setup_ca()
    set_state('pki.available')


@hook('config-changed')
def config_postfix():
    config = hookenv.config()
    if config.changed('hostname'):
        remove_state('pki.cert.issued')
    if config.get('hostname'):
        issue_cert(config['hostname'])
        set_state('pki.cert.issued')


def install_binary(filename):
    local_binary = os.path.join(hookenv.charm_dir(), "files", filename)
    install_binary = "/usr/bin/" + filename
    shutil.copyfile(local_binary, install_binary)
    os.chmod(install_binary, 0o755)


def setup_ca():
    config = hookenv.config()
    pki_dir = os.path.join(hookenv.charm_dir(), "pki")
    if not os.path.exists(pki_dir):
        os.makedirs(pki_dir, 0o600)
    render(source="ca.json",
        target=os.path.join(pki_dir, "ca.json"),
        owner="root",
        perms=0o644,
        context={
            'cfg': config,
        })
    do_cfssl(['/usr/bin/cfssl', 'genkey', '-initca', 'ca.json'], name='ca', cwd=pki_dir)


def do_cfssl(args, name=None, cwd=None):
    cfssljson = subprocess.Popen(['/usr/bin/cfssljson', '-bare', name], stdin=subprocess.PIPE, cwd=cwd)
    cfssl = subprocess.Popen(args, cwd=cwd, stdout=cfssljson.stdin)
    cfssljson.communicate()
    cfssl.wait()
    if cfssl.returncode != 0 or cfssljson.returncode != 0:
        raise Exception("cfssl error")


def issue_cert(hostname):
    pki_dir = os.path.join(hookenv.charm_dir(), "pki")
    public_ip = hookenv.unit_public_ip()
    print public_ip
    render(source="host.csr.json",
        target=os.path.join(pki_dir, "host.csr.json"),
        owner="root",
        perms=0o644,
        context={
            'hostname': hostname,
            'public_ip': public_ip,
        })
    do_cfssl(['/usr/bin/cfssl', 'gencert', '-hostname', hostname, "host.csr.json"],
        name=hostname, cwd=pki_dir)
    with open(os.path.join(pki_dir, 'cert-chain.pem'), 'w') as wf:
        for filename in ('%s.pem' % (hostname), 'ca.pem'):
            with open(os.path.join(pki_dir, filename), 'r') as rf:
                wf.write(rf.read())
    for fn in (shutil.copyfile, shutil.copymode):
        fn(os.path.join(pki_dir, '%s-key.pem' % (hostname)),
            os.path.join(pki_dir, 'host-key.pem'))
