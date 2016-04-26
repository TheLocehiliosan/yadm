# Copyright 1999-2016 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id$

EAPI=6

DESCRIPTION="A dotfile manager for config files in your home folder"
HOMEPAGE="https://github.com/TheLocehiliosan/yadm/"
SRC_URI="https://github.com/TheLocehiliosan/${PN}/archive/${PV}.tar.gz -> ${P}.tar.gz"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86 ~alpha ~arm ~hppa ~ia64 ~ppc ~ppc64 ~s390 ~sh ~sparc"

DOCS=( CHANGES CONTRIBUTORS README.md )

DEPEND="dev-vcs/git
	app-crypt/gnupg"
RDEPEND="${DEPEND}"

src_install() {
	dodoc "${DOCS[@]}"

	dobin yadm
	doman yadm.1
}
