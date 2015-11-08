
all: files/cfssl files/cfssljson

files/%: ../../cfssl/bin/%
	cp $< $@

../../cfssl/bin/%:
	make -C ../../cfssl

clean:
	$(RM) files/cfssl files/cfssljson

.PHONY: all clean

