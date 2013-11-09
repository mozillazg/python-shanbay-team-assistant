.DEFAULT: exe

exe:
	@echo "make assistant.exe"
	"e:\Python27\Scripts\pyinstaller.exe" assistant.spec
# 
# publish:
# 	@echo "publish to pypi"
# 	python setup.py publish
# 
# register:
# 	@echo "register to pypi"
# 	python setup.py register
