# SCRIPT Python  utilisé dans texmath-gif.sty pour mettre à jour les gif
# lors de la compilation. Les imports personnels sont relatifs au dossier
# contenant le script update_gif.py
import re
import subprocess
from src.tools import update_last_run_date, get_last_run_date, DATA_DIR, get_exe

folder_path = DATA_DIR / "graphics" / "gif"
output_folder = folder_path / "data"
magick = get_exe('magick')

last_run_time = get_last_run_date(__file__)

# Lister les fichiers .gif récursivement
gif_files = []
png0_files = []
for file_path in folder_path.rglob('*'):
    matches = re.findall('.gif$', str(file_path))
    if matches:
        gif_files.append(file_path)
    else:
        matches = re.findall('-0.png$', str(file_path))
        if matches:
            png0_files.append(file_path.name[:-6])

# Filtrer les fichiers modifiés après la dernière exécution
recent_files = []
for file_path in gif_files:
    print(output_folder / (file_path.stem + "-FrameNumber.txt"))
    if file_path.stat().st_mtime > last_run_time.timestamp() or not file_path.stem in png0_files:
        recent_files.append(file_path)
    elif not (output_folder / (file_path.stem + "-FrameNumber.txt")).exists():
        recent_files.append(file_path)
    # Si il manque un fichier png, ajouter a recent file


print(folder_path)
for file in recent_files:
    
    output_png = output_folder / (file.stem + ".png")

    # Commande conversion GIF -> PNG
    cmd_convert = [
        magick,
        str(file),
        "-coalesce",
        "+repage",
        str(output_png)
    ]

    print("Exécution de la commande :", " ".join(cmd_convert))
    subprocess.run(cmd_convert, check=True)

    print("Exécution de la commande :", " ".join(cmd_convert))
    subprocess.run(cmd_convert, check=True)

    # Générer fichier nombre de frames - 1
    
    file_frame_number = output_folder / (file.stem + "-FrameNumber.txt")
    # 2. Compter le nombre de PNG générés
    generated_files = list(output_folder.glob(f"{file.stem}-*.png"))
    num_frames = len(generated_files)

    # 3. Écrire le nombre de frames dans un fichier
    file_frame_number = output_folder / (file.stem + "-FrameNumber.txt")
    file_frame_number.parent.mkdir(parents=True, exist_ok=True)
    file_frame_number.write_text(str(num_frames-1), encoding="utf-8")

    print(f"{num_frames} frames générées et écrites dans {file_frame_number}")

    # Lire le contenu et nettoyer les caractères non ASCII imprimables
    with open(file_frame_number, "r", encoding="utf-8") as f:
        content = f.read()

    clean_content = "".join(c for c in content if 32 <= ord(c) <= 126)

    with open(file_frame_number, "w", encoding="utf-8") as f:
        f.write(clean_content)

# Mettre à jour la date de dernière exécution
update_last_run_date(__file__)
