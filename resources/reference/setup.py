from cx_Freeze import setup, Executable
import os
includes = ['pyglet.clock', 'pyglet.resource', 'pyglet.graphics', 'pyglet.gl', 'pyglet.sprite', 'pymunk']
excludes = []
packages = []
lib_path = []

setup( name = "test" , 
	version = "0.1" , 
	description = "test" , 
	options = {"build_exe":{"includes": includes,
							"excludes": excludes,
							"packages": packages,
							"path": lib_path}},
	executables = [Executable(script = "main.py", base = "Win32GUI")])