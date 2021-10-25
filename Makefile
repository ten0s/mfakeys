all: chromedriver venv build

chromedriver: bin/chromedriver

bin/chromedriver:
	# https://chromedriver.chromium.org/downloads
	wget --continue https://chromedriver.storage.googleapis.com/95.0.4638.17/chromedriver_linux64.zip
	unzip chromedriver_linux64.zip -d bin/

venv:
	virtualenv --python python3 venv
	venv/bin/pip install -r requirements.txt

build: mfakeys.py
	venv/bin/pyinstaller --onefile --add-binary "bin/chromedriver:bin" mfakeys.py

clean:
	rm -rf bin/ build/ dist/ venv/ *.pyc *.spec *.zip
