# -*- mode: python -*-

block_cipher = None


a = Analysis(['getspotlightimages.py'],
             pathex=['C:\\Users\\Travis Clinkscales\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\cv2\\opencv_ffmpeg400.dll', 'C:\\Users\\Travis Clinkscales\\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\shutil.py', 'D:\\Github\\GetImages'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='getspotlightimages',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='getspotlightimages')
