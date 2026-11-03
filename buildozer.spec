[app]
title = My Daily Life
package.name = mydailylife
package.domain = org.mydailylife

source.dir = .
source.include_exts = py,json,png,jpg,jpeg,kv,atlas
version = 1.0.1

requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,POST_NOTIFICATIONS
android.api = 33
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2
p4a.url = https://github.com/kivy/python-for-android.git
p4a.commit = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
