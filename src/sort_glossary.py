import sys
WORDLIST_PATH = sys.argv[1]
SORTEDINDEX_PATH = sys.argv[2]
WORDLISTFOLDER = ""
with open(WORDLIST_PATH, 'r') as wordlistfile :
    READ = wordlistfile.read()
SORTEDINDEX = []
def sorted_index(LIST):
    for value, index in sorted((v,i) for i,v in enumerate(LIST)):
        SORTEDINDEX.append(str(index))
READ_SPLIT = READ.split('\n')[:-1]
READ_TO_EVAL = READ_SPLIT[0] + ','.join(map(lambda s:"\'" + s + "\'", READ_SPLIT[1:-1])) + READ_SPLIT[-1]
LIST_TO_SORT = eval(READ_TO_EVAL)
sorted_index(LIST_TO_SORT)
with open(SORTEDINDEX_PATH,'w') as sortedIndexFile:
    sortedIndexFile.write(','.join(SORTEDINDEX) + '%')