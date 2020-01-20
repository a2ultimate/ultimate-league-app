#!/bin/bash
function p {
  local dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"
  echo $dir
}
p
