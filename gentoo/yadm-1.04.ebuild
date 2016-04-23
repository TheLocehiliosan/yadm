# Copyright 1999-2016 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id$

EAPI=5

DESCRIPTION="Yet Another Dotfiles Manager"
HOMEPAGE="https://github.com/TheLocehiliosan/yadm/"
SRC_URI="https://github.com/TheLocehiliosan/${PN}/archive/${PV}.tar.gz -> ${P}.tar.gz"

LICENSE="GPLv3"
SLOT="0"
KEYWORDS="amd64 x86 ~alpha ~arm ~hppa ~ia64 ~ppc ~ppc64 ~s390 ~sh ~sparc"
IUSE="doc"

DOCS=( CHANGES CONTRIBUTORS yadm.md README.md )

DEPEND="dev-vcs/git
app-shells/bash"
RDEPEND="${DEPEND}"

src_compile() {
  # Bash scripts don't need to compile
  true
}

src_install() {
  if use doc; then
    dodoc "${DOCS[@]}"
  fi

  dobin yadm
  doman yadm.1
}

