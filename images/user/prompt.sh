# a shorter default prompt for login shells (jupyterlab terminals, ssh)
# debian's default is user@hostname, which is always jovyan on the pod name,
# e.g. jovyan@jupyter-minrk-berkeley-edu---dc9ed9d1:~$
#
# sourced after mamba.sh, so this replaces the prompt env activation leaves.
# `mamba activate` still adds its own `(env) ` prefix on top of it,
# and a PS1 set in your own shell config still wins over this default.

# these are bash prompt escapes, and only interactive shells have a prompt
[ -n "${BASH_VERSION:-}" ] || return
case $- in
    *i*) ;;
    *) return ;;
esac

case "${TERM:-dumb}" in
    dumb)
        PS1='\w \$ '
        ;;
    *)
        # working directory in bold blue
        PS1='\[\e[1;34m\]\w\[\e[0m\] \$ '
        ;;
esac
