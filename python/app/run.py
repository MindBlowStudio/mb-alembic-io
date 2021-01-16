import os
import time


path = os.path.dirname(__file__)
file = os.path.join(path, 'export.py')
dir = 'R:\\Zombie Dropbox\\PROJETOS\\2021\\1881_LORIN_SPINOFF'
dir = dir.replace(' ', '-')
cmd = 'start cmd /k %MAYA_PYTHON% {file} {shot} {project} {path} {locale}'.format(file=file, shot=1354, project=297, path=dir, locale='06_prod_anim')
os.system(cmd)