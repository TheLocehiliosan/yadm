.PHONY: all
all: yadm.md contrib

yadm.md: yadm.1
	@groff -man -Tascii ./yadm.1 | col -bx | sed 's/^[A-Z]/## &/g' | sed '/yadm(1)/d' > yadm.md

.PHONY: contrib
contrib:
	@echo "CONTRIBUTORS\n" > CONTRIBUTORS
	@git shortlog -ns master gh-pages dev dev-pages | cut -f2 >> CONTRIBUTORS

.PHONY: pdf
pdf:
	@groff -man -Tps ./yadm.1 > yadm.ps
	@open yadm.ps
	@sleep 1
	@rm yadm.ps

.PHONY: test
test: bats shellcheck

.PHONY: parallel
parallel:
	ls test/*bats | time parallel -q -P0 -- docker run --rm -v "$$PWD:/yadm:ro" yadm/testbed bash -c 'bats {}'

.PHONY: bats
bats:
	@echo Running all bats tests
	@GPG_AGENT_INFO= bats test

.PHONY: shellcheck
shellcheck:
	@echo Running shellcheck
	@shellcheck --version || true
	@shellcheck -s bash yadm bootstrap test/*.bash completion/yadm.bash_completion
	@cd test; \
	for bats_file in *bats; do \
		sed 's/^@test.*{/function test() {/' "$$bats_file" > "/tmp/$$bats_file.bash"; \
		shellcheck -s bash "/tmp/$$bats_file.bash"; \
		test_result="$$?"; \
		rm -f "/tmp/$$bats_file.bash"; \
		[ "$$test_result" -ne 0 ] && exit 1; \
	done; true

.PHONY: testhost
testhost:
	@target=HEAD
	@rm -rf /tmp/testhost
	@git show $(target):yadm > /tmp/testhost
	@chmod a+x /tmp/testhost
	@echo Starting testhost target=\"$$target\"
	@docker run -w /root --hostname testhost --rm -it -v "/tmp/testhost:/bin/yadm:ro" yadm/testbed:latest bash

.PHONY: man
man:
	groff -man -Tascii ./yadm.1 | less

.PHONY: wide
wide:
	man ./yadm.1
