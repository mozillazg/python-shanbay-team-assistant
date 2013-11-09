.DEFAULT: py2exe

pyinstaller:
	@echo "make assistant.exe"
	"e:\Python27\Scripts\pyinstaller.exe" assistant.spec

py2exe:
	@echo "py2exe"
	python setup.py py2exe
# 
# publish:
# 	@echo "publish to pypi"
# 	python setup.py publish
# 
# register:
# 	@echo "register to pypi"
# 	python setup.py register
