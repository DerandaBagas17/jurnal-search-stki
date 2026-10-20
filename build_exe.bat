@echo off
echo ========================================================
echo Memulai Kompilasi JurnalSearch PDF Menjadi File .EXE...
echo ========================================================

python -m PyInstaller --noconsole --onefile --name "JurnalSearch_PDF" --add-data "journals.json;." --collect-all customtkinter app.py

echo.
echo ========================================================
echo Kompilasi Selesai!
echo File .EXE Anda tersedia di folder:
echo dist\JurnalSearch_PDF.exe
echo ========================================================
pause
