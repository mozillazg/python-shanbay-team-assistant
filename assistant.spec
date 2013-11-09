# -*- mode: python -*-
def Datafiles(*filenames, **kw):
    import os

    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

a = Analysis(['assistant.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='assistant.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          # icon='shanbay.ico'
          )

# docfiles = Datafiles('LICENSE-GPLv3.txt', 'doc/pdfposter.html')
# dbfile = Datafiles('db/countries.db', strip_path=False) # keep the path of this file
# coll = COLLECT(exe,
#                a.binaries,
#                a.zipfiles,
#                a.datas,
#                docfiles,
#                dbfile,
#                name=os.path.join('dist', 'pdfposter'))
