import sys
from pathlib import Path
sys.path.insert(0, r"f:\Root\Projects\texmaths")
from src import impress

# Forcer le format en A5 Portrait
impress.get_pdf_format = lambda p: "A5 Portrait"

# Stub subprocess.run pour éviter d'appeler Ghostscript
def fake_run(args, stdout=None, stderr=None):
    print("FAKE subprocess.run called with:", args)
    class R: pass
    R.returncode = 0
    return R()

impress.subprocess.run = fake_run

res = impress.extract_big(Path("somecourse.pdf"))
print("extract_big returned:", res)
print("expected suffix '-big.pdf':", str(res).endswith('-big.pdf') if res else None)
print("TMP_DIR:", impress.TMP_DIR)
