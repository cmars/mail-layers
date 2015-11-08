
JUJU_REPOSITORY := $(shell pwd)

all: cfssl mailbox

cfssl:
	$(MAKE) -C cfssl

mailbox:
	(cd layers/mailbox; JUJU_REPOSITORY=$(JUJU_REPOSITORY) charm build)

clean:
	#$(MAKE) -C cfssl clean
	$(RM) -r trusty

.PHONY: all cfssl clean mailbox

