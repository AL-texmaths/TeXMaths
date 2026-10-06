import os
import sys

WORDLIST_PATH = sys.argv[1]

SORTEDINDEX_PATH = sys.argv[2]

try:
    os.remove(SORTEDINDEX_PATH)
except FileNotFoundError:
    pass

with open(WORDLIST_PATH, 'r', encoding='utf-8') as wordlistfile:
    lines = wordlistfile.read().splitlines()

if len(lines) < 2 or lines[0].strip() != '[' or lines[-1].strip() != ']':
    raise ValueError(f"Invalid word list format in {WORDLIST_PATH}")

words = [word.strip() for word in lines[1:-1]]
sorted_indices = sorted(range(len(words)), key=lambda index: words[index])

with open(SORTEDINDEX_PATH, 'w', encoding='utf-8') as sorted_index_file:
    sorted_index_file.write(','.join(map(str, sorted_indices)) + '%')