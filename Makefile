DESTDIR ?= /

PREFIXBIN=$(DESTDIR)/usr/bin
PREFIXSHARE=$(DESTDIR)/usr/share/gamesreport

install:
	install -o root -d $(PREFIXBIN)
	install -o root -d $(PREFIXSHARE)
	install -m 755 -o root gamesreport.py $(PREFIXBIN)/gamesreport
	install -m 644 -o root report.odt ${PREFIXSHARE}

uninstall:
	rm $(PREFIXBIN)/gamesreport
	rm $(PREFIXSHARE)
