all: yadm.md contrib

yadm.md: yadm.1
	@groff -man -Tascii ./yadm.1 | col -bx | sed 's/^[A-Z]/## &/g' | sed '/yadm(1)/d' > yadm.md

contrib:
	@echo "CONTRIBUTORS\n" > CONTRIBUTORS
	@git shortlog -ns | cut -f2 >> CONTRIBUTORS

pdf:
	@groff -man -Tps ./yadm.1 > yadm.ps
	@open yadm.ps
	@sleep 1
	@rm yadm.ps

.PHONY: test
test: bats shellcheck

.PHONY: bats
bats:
	@echo Running all bats tests
	@GPG_AGENT_INFO= bats test

.PHONY: shellcheck
shellcheck:
	@echo Running shellcheck
	@shellcheck --version || true
	@shellcheck -s bash yadm test/*.bash
	@for bats_file in test/*bats; do \
		sed 's/^@test.*{/function test() {/' "$$bats_file" > "$$bats_file .bash"; \
		shellcheck -s bash "$$bats_file .bash"; \
		test_result="$$?"; \
		rm -f "$$bats_file .bash"; \
		[ "$$test_result" -ne 0 ] && exit 1; \
	done; true

man:
	groff -man -Tascii ./yadm.1 | less

wide:
	man ./yadm.1
