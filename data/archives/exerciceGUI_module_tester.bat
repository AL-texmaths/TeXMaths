cd /d \Root
call Envs\texmaths\Scripts\activate
cd /d Projets\TeXMaths

python -m src.tools
python -m src.extract_preview
python -m src.check_database
python -m src.update_data_index
python exerciceGUI.py
pause