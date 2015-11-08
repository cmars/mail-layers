import os

from charmhelpers.core import hookenv


def certkey():
	pki_dir = os.path.join(hookenv.charm_dir(), 'pki')
	return {
		'certfile': os.path.join(pki_dir, 'cert-charm.pem'),
		'keyfile': os.path.join(pki_dir, 'host-key.pem'),
	}
