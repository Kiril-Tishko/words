#!/usr/bin/env bash
# Downloads the open word lists used to find English–Ukrainian identical words.
# Files go to $SRC (default: ../sources next to the repo). They are NOT committed (large, other licenses).
set -euo pipefail
SRC="${SRC:-$(cd "$(dirname "$0")/../.." && pwd)/sources}"
mkdir -p "$SRC" && cd "$SRC"
get() { [ -s "$(basename "$1")" ] || curl -sSfLO "$1"; }

# English
get https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt            # ~370k words incl. archaic
get https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict                 # pronunciations
get https://raw.githubusercontent.com/LibreOffice/dictionaries/master/en/en_US.dic          # US spelling dictionary
get https://raw.githubusercontent.com/LibreOffice/dictionaries/master/en/en_GB.dic          # UK spelling dictionary
get https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_50k.txt
# CEFR levels (CC BY-SA 4.0): CEFR-J A1–B2 + Octanove C1–C2
get https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv
get https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/octanove-vocabulary-profile-c1c2-1.0.csv

# Ukrainian
get https://raw.githubusercontent.com/LibreOffice/dictionaries/master/uk_UA/uk_UA.dic       # hunspell
get https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/uk/uk_50k.txt
get https://kaikki.org/dictionary/Ukrainian/kaikki.org-dictionary-Ukrainian.jsonl           # Wiktionary (glosses, etymology)
[ -d dict_uk ] || GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/brown-uk/dict_uk dict_uk   # VESUM

# Frequencies for both languages come from the `wordfreq` Python package (pip install wordfreq rapidfuzz)
echo "Sources ready in $SRC"
