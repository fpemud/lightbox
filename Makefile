PACKAGE_VERSION=0.0.1
prefix=/usr

clean:
	find . -name *.pyc | xargs rm -f

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/bin"
	install -m 0755 lightbox "$(DESTDIR)/$(prefix)/bin"

	install -d -m 0755 "$(DESTDIR)/$(prefix)/lib/lightbox"
	cp -r lib/* "$(DESTDIR)/$(prefix)/lib/lightbox"
	find "$(DESTDIR)/$(prefix)/lib/lightbox" -type f | xargs chmod 644
	find "$(DESTDIR)/$(prefix)/lib/lightbox" -type d | xargs chmod 755

uninstall:
	rm -Rf "$(DESTDIR)/$(prefix)/bin/lightbox"
	rm -Rf "$(DESTDIR)/$(prefix)/lib/lightbox"

.PHONY: all clean install uninstall
