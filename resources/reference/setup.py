from cx_Freeze import setup, Executable
import os
# When building, copy everything from lib/ to the 
# directory where main.py is. That way there is no module
# missing error when cx_freeze tries to import all of the
# modules it can not find. Placing them in the same directory
# allows cx_freeze to find them.
# It should look like main.py, player.py, levelassembler.py
# all in the same directory.
include_files = ['resources/','levels/','chipmunk.dll']
includes = ['pymunk','configparser'] #'pyglet.clock', 'pyglet.resource', 'pyglet.graphics', 'pyglet.gl', 'pyglet.sprite', 'pyglet.image',
excludes = ['OpenGL']
packages = ['pyglet']
path = []#['libs/']


setup( 	name = "Fragile Truck", 
		version = "0.0.1", 
		description = "Physics Game", 
		author = 'Everett Walls',
		options = {'build_exe':
							{'include_files':include_files,
							 'includes':includes,
							 'excludes':excludes,
							 'packages':packages}
							 },
		executables = [Executable(script = "main.py", 
								  base = "Win32GUI", 
								  targetName = "truck.exe",
								  copyDependentFiles = True,
								  #appendScriptToExe = True,
								  #compress = True,
								  #path = path,
								  )]
)