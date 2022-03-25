all: chromedriver env build

chromedriver: bin/chromedriver

bin/chromedriver:
	# https://chromedriver.chromium.org/downloads
	wget --continue https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip
	unzip chromedriver_linux64.zip -d bin/

env:
	python3 -m venv env
	env/bin/pip install -r requirements.txt

build: mfakeys.py
	env/bin/pyinstaller --onefile --add-binary "bin/chromedriver:bin" mfakeys.py

clean:
	rm -rf bin/ build/ dist/ env/ *.pyc *.spec *.zip
