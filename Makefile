#!/usr/bin/make -f

package=firefox-solydxk-adjustments

.PHONY: all build clean update

all: build

build: update

clean:

update:
	python3 download.py