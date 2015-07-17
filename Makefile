all: yadm.md

yadm.md: yadm.1
	@groff -man -Tascii ./yadm.1 | col -bx | sed 's/^[A-Z]/## &/g' | sed '/yadm(1)/d' > yadm.md

pdf:
	@groff -man -Tps ./yadm.1 > yadm.ps
	@open yadm.ps
	@sleep 1
	@rm yadm.ps

man:
	groff -man -Tascii ./yadm.1 | less

wide:
	man ./yadm.1
