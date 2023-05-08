@echo on

pip install -r requirements.txt
pyinstaller --onefile --noconsole --windowed --icon=steam.ico main.py

pause