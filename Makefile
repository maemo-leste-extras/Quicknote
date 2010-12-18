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
TAG_FILE=~/.ctags/$(PROJECT_NAME).tags
TODO_FILE=./TODO

DEBUGGER=winpdb
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

package: $(OBJ) build_mo
	rm -Rf $(BUILD_PATH)

	mkdir -p $(BUILD_PATH)/generic
	cp $(SOURCE_PATH)/constants.py $(BUILD_PATH)/generic
	cp $(PROGRAM)  $(BUILD_PATH)/generic
	$(foreach file, $(DATA), cp $(file) $(BUILD_PATH)/generic/$(subst /,-,$(file)) ; )
	$(foreach file, $(SOURCE), cp $(file) $(BUILD_PATH)/generic/$(subst /,-,$(file)) ; )
	#$(foreach file, $(OBJ), cp $(file) $(BUILD_PATH)/generic/$(subst /,-,$(file)) ; )
	$(foreach file, $(LOCALE_FILES), cp $(file) $(BUILD_PATH)/generic/$(subst /,-,$(file)) ; )
	cp data/$(PROJECT_NAME).desktop $(BUILD_PATH)/generic
	cp data/$(PROJECT_NAME).service $(BUILD_PATH)/generic
	cp data/low/$(PROJECT_NAME).png $(BUILD_PATH)/generic/26x26-$(PROJECT_NAME).png
	cp data/40/$(PROJECT_NAME).png $(BUILD_PATH)/generic/40x40-$(PROJECT_NAME).png
	cp data/48/$(PROJECT_NAME).png $(BUILD_PATH)/generic/48x48-$(PROJECT_NAME).png
	cp data/scale/$(PROJECT_NAME).png $(BUILD_PATH)/generic/scale-$(PROJECT_NAME).png
	cp support/builddeb.py $(BUILD_PATH)/generic
	cp support/py2deb.py $(BUILD_PATH)/generic
	cp support/fake_py2deb.py $(BUILD_PATH)/generic

	mkdir -p $(BUILD_PATH)/diablo
	cp -R $(BUILD_PATH)/generic/* $(BUILD_PATH)/diablo
	cd $(BUILD_PATH)/diablo ; python builddeb.py diablo
	mkdir -p $(BUILD_PATH)/fremantle
	cp -R $(BUILD_PATH)/generic/* $(BUILD_PATH)/fremantle
	cd $(BUILD_PATH)/fremantle ; python builddeb.py fremantle
	mkdir -p $(BUILD_PATH)/debian
	cp -R $(BUILD_PATH)/generic/* $(BUILD_PATH)/debian
	cd $(BUILD_PATH)/debian ; python builddeb.py debian

upload:
	dput fremantle-extras-builder $(BUILD_PATH)/fremantle/$(PROJECT_NAME)*.changes
	dput diablo-extras-builder $(BUILD_PATH)/diablo/$(PROJECT_NAME)*.changes
	cp $(BUILD_PATH)/debian/*.deb ./www/$(PROJECT_NAME).deb

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
