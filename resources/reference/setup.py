from cx_Freeze import setup, Executable
import os
includes = ['pyglet.clock', 'pyglet.resource', 'pyglet.graphics', 'pyglet.gl', 'pyglet.sprite', 'pyglet.image',
			'pymunk','configparser']
excludes = []
packages = ['pyglet']
lib_path = ['libs/']

setup( 	name = "Fragile Truck" , 
		version = "0.0.1" , 
		description = "Everett Walls" , 
		options = {'build_exe':
							{'includes':includes,
							 'packages':packages}
							 },
		executables = [Executable(script = "main.py", 
								  base = "Win32GUI", 
								  targetName = "truck.exe",
								  copyDependentFiles = True,
								  appendScriptToExe = True,
								  compress = True,)])