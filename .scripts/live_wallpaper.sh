#!/bin/bash
_screen() {
    xwinwrap -ov -g $1 -- mpv --fullscreen\
	--hwdec=auto --vo=gpu --hwdec-codecs=all \
        --on-all-workspaces --no-keepaspect-window \
        --no-stop-screensaver --no-input-default-bindings \
	--no-sub --no-window-dragging  --no-config \
	--panscan=1.0 \
        --loop-file --no-audio --no-osc --no-osd-bar -wid WID --quiet \
        "$2" --background="$3" --video-zoom="$4" &
}

killall xwinwrap mpv

sleep 0.5

for i in $( xrandr -q | grep ' connected' | grep -oP '\d+x\d+\+\d+\+\d+')
do
    _screen $i "$1" "${2:-#000000}" "${3:-0}"
done
