PROJECT_NAME=quicknote
PROJECT_VERSION=0.7.8
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
STYLE_TEST=../../Python/tools/pep8.py --ignore=W191,E501
LINT_RC=./support/pylint.rc
LINT=pylint --rcfile=$(LINT_RC)
PROFILE_GEN=python -m cProfile -o .profile
PROFILE_VIEW=python -m pstats .profile
TODO_FINDER=support/todo.py
CTAGS=ctags-exuberant

.PHONY: all run profile debug test lint tags todo clean distclean install update_po build_mo

all: test

run: $(OBJ)
	$(PROGRAM)

profile: $(OBJ)
	$(PROFILE_GEN) $(PROGRAM)
	$(PROFILE_VIEW)

debug: $(OBJ)
	$(DEBUGGER) $(PROGRAM)

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

tags: $(TAG_FILE) 

todo: $(TODO_FILE)

clean:
	rm -rf ./locale
	rm -Rf $(OBJ)
	rm -Rf $(BUILD_PATH)
	rm -Rf $(TODO_FILE)

distclean:
	rm -Rf $(OBJ)
	rm -Rf $(BUILD_PATH)
	rm -Rf $(TAG_FILE)
	find $(SOURCE_PATH) -name "*.*~" | xargs rm -f
	find $(SOURCE_PATH) -name "*.swp" | xargs rm -f
	find $(SOURCE_PATH) -name "*.bak" | xargs rm -f
	find $(SOURCE_PATH) -name ".*.swp" | xargs rm -f

$(TAG_FILE): $(OBJ)
	mkdir -p $(dir $(TAG_FILE))
	$(CTAGS) -o $(TAG_FILE) $(SOURCE)

$(TODO_FILE): $(SOURCE)
	@- $(TODO_FINDER) $(SOURCE) > $(TODO_FILE)

%.pyc: %.py
	$(SYNTAX_TEST) $<

#Makefile Debugging
#Target to print any variable, can be added to the dependencies of any other target
#Userfule flags for make, -d, -p, -n
print-%: ; @$(error $* is $($*) ($(value $*)) (from $(origin $*)))
