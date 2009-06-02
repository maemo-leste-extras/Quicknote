PROJECT_NAME=quicknote
PROJECT_VERSION=0.7.7
SOURCE_PATH=src
SOURCE=$(shell find $(SOURCE_PATH) -iname "*.py")
LOCALE_PATH=locale
LOCALE_FILES=$(shell find $(LOCALE_PATH) -iname "*.mo")
PROGRAM=$(SOURCE_PATH)/$(PROJECT_NAME).py
OBJ=$(SOURCE:.py=.pyc)
BUILD_PATH=./builddeb/

TEXT_DOMAIN=$(PROJECT_NAME)
POTFILES=$(wildcard src/quicknoteclasses/*.py)

UNIT_TEST=nosetests --with-doctest -w .
SYNTAX_TEST=support/test_syntax.py
LINT_RC=./support/pylint.rc
LINT=pylint --rcfile=$(LINT_RC)
PROFILE_GEN=python -m cProfile -o .profile
PROFILE_VIEW=python -m pstats .profile

.PHONY: all run profile test lint clean distclean install update_po build_mo

all: build_mo
	python2.5 setup.py build  

run:
	$(PROGRAM)

profile:
	$(PROFILE_GEN) $(PROGRAM)
	$(PROFILE_VIEW)

test: $(OBJ)
	$(UNIT_TEST)

package: clean $(OBJ) all
	dpkg-buildpackage -rfakeroot 
	dpkg -i ../$(PROJECT_NAME)_$(PROJECT_VERSION)_all.deb

update_po: po/templates.pot
	@for lang in $(basename $(notdir $(wildcard po/*.po))); do \
		msgmerge -U --strict --no-wrap po/$$lang.po po/templates.pot; \
	done

po/templates.pot: $(POTFILES)
	xgettext --language=Python --strict --no-wrap --output=$@ $(POTFILES)

build_mo:
	@for lang in $(basename $(notdir $(wildcard po/*.po))); do \
		mkdir -p locale/$$lang/LC_MESSAGES; \
		msgfmt --statistics -c -o locale/$$lang/LC_MESSAGES/$(TEXT_DOMAIN).mo po/$$lang.po; \
	done

build: $(OBJ) build_mo
	rm -Rf $(BUILD_PATH)
	mkdir $(BUILD_PATH)
	cp $(PROGRAM)  $(BUILD_PATH)
	cp src/constants.py $(BUILD_PATH)
	$(foreach file, $(DATA), cp $(file) $(BUILD_PATH)/$(subst /,-,$(file)) ; )
	$(foreach file, $(SOURCE), cp $(file) $(BUILD_PATH)/$(subst /,-,$(file)) ; )
	$(foreach file, $(OBJ), cp $(file) $(BUILD_PATH)/$(subst /,-,$(file)) ; )
	$(foreach file, $(LOCALE_FILES), cp $(file) $(BUILD_PATH)/$(subst /,-,$(file)) ; )
	cp data/$(PROJECT_NAME).desktop $(BUILD_PATH)
	cp data/$(PROJECT_NAME).service $(BUILD_PATH)
	cp data/low/$(PROJECT_NAME).png $(BUILD_PATH)/26x26-$(PROJECT_NAME).png
	cp data/40/$(PROJECT_NAME).png $(BUILD_PATH)/40x40-$(PROJECT_NAME).png
	cp data/48/$(PROJECT_NAME).png $(BUILD_PATH)/48x48-$(PROJECT_NAME).png
	cp data/scale/$(PROJECT_NAME).png $(BUILD_PATH)/scale-$(PROJECT_NAME).png
	cp support/builddeb.py $(BUILD_PATH)
	cp support/fake_py2deb.py $(BUILD_PATH)

lint: $(OBJ)
	$(foreach file, $(SOURCE), $(LINT) $(file) ; )

clean: 
	rm -rf ./locale
	rm -rf $(OBJ)
	rm -Rf $(BUILD_PATH)
	python2.5 setup.py clean --all

distclean: clean
	find $(SOURCE_PATH) -name "*.*~" | xargs rm -f
	find $(SOURCE_PATH) -name "*.swp" | xargs rm -f
	find $(SOURCE_PATH) -name "*.bak" | xargs rm -f
	find $(SOURCE_PATH) -name ".*.swp" | xargs rm -f

install: build_mo
	python2.5 setup.py install --root $(DESTDIR) 

%.pyc: %.py
	$(SYNTAX_TEST) $<

#Makefile Debugging
#Target to print any variable, can be added to the dependencies of any other target
#Userfule flags for make, -d, -p, -n
print-%: ; @$(error $* is $($*) ($(value $*)) (from $(origin $*)))
