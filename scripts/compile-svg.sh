#!/bin/bash

function svg-compile() {
    local from=buddyup/svg/$1.svg
    local to=buddyup/static/img/${1}-${2}x${3}.png
    echo $from "->" $to
    rsvg-convert -w $2 -h $3 -o $to $from
}

# Compile upvote/downvote

for name in {upvote,downvote}-{active,inactive}; do
    svg-compile $name 40 20
done

svg-compile linkedin 50 50
