from src.tools import LATEX_DIR

enonces_path = LATEX_DIR / "enonces"
output_path = LATEX_DIR / "catalogues" / "enonces.tex"

outputdatas = ''
file_pathes = []
for file_path in enonces_path.rglob('*.tex'):
    file_pathes.append(file_path)
file_pathes.sort()
for file_path in file_pathes:
    outputdata = r"\catalogues@enonce " + str(file_path.relative_to(enonces_path)).replace('\\', '/')+'\n'
    outputdatas += outputdata
    print(f'writing \n{outputdata[:-1]}\n in {output_path}')
with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write(outputdatas)