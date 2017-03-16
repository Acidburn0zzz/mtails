# This library is meant to be used in bash, with "set -e" and "set -u".

BASE_BRANCHES="stable testing devel feature/stretch"

# Returns "" if in undetached head
git_current_branch() {
	local git_ref
	if git_ref="$(git symbolic-ref HEAD 2>/dev/null)"; then
		echo "${git_ref#refs/heads/}"
	else
		echo ""
	fi
}

git_in_detached_head() {
	[ -z "$(git_current_branch)" ]
}

# Returns "" if ref does not exist
git_commit_from_ref() {
	git rev-parse --verify "${@}" 2>/dev/null || :
}

git_current_commit() {
	git_commit_from_ref "${@}" HEAD
}

# Returns "" if not a tag
git_tag_from_commit() {
	git describe --tags --exact-match "${1}" 2>/dev/null || :
}

# Returns "" if not on a tag
git_current_tag() {
	git_tag_from_commit $(git_current_commit)
}

# Try to describe what currently is checked out. Returns "" (i.e. no
# way to describe it) if Git HEAD is not tagged and if we are in
# detached HEAD
git_current_head_name() {
	if git_in_detached_head; then
		git_current_tag
	else
		git_current_branch
	fi
}

git_on_a_tag() {
	[ -n "$(git_current_tag)" ]
}

base_branch() {
	cat config/base_branch | head -n1
}

base_branches() {
	echo ${BASE_BRANCHES}
}

on_base_branch() {
	for base_branch in $BASE_BRANCHES ; do
		if [ "$(git_current_branch)" = "${base_branch}" ] ; then
			return 0
		fi
	done

	return 1
}

branch_name_to_suite() {
	local branch="$1"

	echo "$branch" | sed -e 's,[^.a-z0-9-],-,ig'  | tr '[A-Z]' '[a-z]'
}

fatal() {
	echo "$*" >&2
	exit 1
}

git_tag_exists() {
	local tag="$1"

	test -n "$(git tag -l "$tag")"
}

version_was_released() {
	local version="$1"

	version="$(echo "$version" | tr '~' '-')"
	git_tag_exists "$version"
}

version_in_changelog() {
	dpkg-parsechangelog | awk '/^Version: / { print $2 }'
}

previous_version_in_changelog() {
	dpkg-parsechangelog --offset 1 --count 1 | awk '/^Version: / { print $2 }'
}

# Make it so that when this script is called, any function defined in
# this script can be invoked via arguments, e.g.:
#
# $ auto/scripts/utils.sh git_commit_from_ref 3.0-beta2
# eca83a88a9dd958b16b4d5b04fea3ea503a3815d
#
if [ "$(basename ${0})" = utils.sh ] && [ -n "${1}" ]; then
	if grep -q "^${1}() {$" "${0}"; then
		eval "\"\${@}\""
	else
		echo "unknown shell function: ${1}" >&2
		exit 1
	fi
fi
