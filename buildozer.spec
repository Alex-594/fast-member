[app]

# (str) Title of your application
title = FAST Member

# (str) Package name
package.name = fastmember

# (str) Package domain (needed for android/ios packaging)
package.domain = org.fastmember

# (str) Source code where the main.py live
source.dir = .

# (str) Main entry point of your application
source.main = FAST_member.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# Упрощенные зависимости для первой сборки
requirements = python3,cython,kivy==2.1.0,plyer,android,pyjnius
# qrcode и cryptography могут потребовать дополнительной настройки

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
# android.sdk = 33  # Deprecated, игнорируется

# (str) Android build tools version (используем стабильную версию)
# android.build_tools_version = 34.0.0

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

