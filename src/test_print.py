import sys
print('bonjour')
with open("G:/test_print_out.txt", 'w', encoding='utf8') as f:
    if len(sys.argv) > 1:
        f.write(sys.argv[1])
    else:
        f.write('null')