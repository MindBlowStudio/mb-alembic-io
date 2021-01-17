import json
import logging
import os
import sys
import time

import maya.cmds as cmds
import maya.standalone
import shotgun_api3

project_id = int(sys.argv[2])
path = sys.argv[3]
path = path.replace('-', ' ').replace('\\', '/')
shot_id = int(sys.argv[1])
locale = str(sys.argv[4])

print('-------------------------------------------------------------------------------------------------------')
print(' CONNETING SHOTGUN API PLEASE WAIT...')
print('-------------------------------------------------------------------------------------------------------')
sg = shotgun_api3.Shotgun("https://mindblow.shotgunstudio.com/", login="support@mindblowstudio.com", password="@Brain123")
print(' -->CONNECTED')
shot = sg.find_one("Shot", filters=[
    ["project.Project.id", "is", project_id],
    ["id", "is", shot_id], ['sg_exported', 'is', 'True']],
                   fields=['code', 'sg_filename', 'sg_file_version', 'sg_root', 'sg_exported', 'sg_sequence', 'project', 'sg_cut_in', 'sg_cut_out'])
projectId = sg.find_one("Project", [['id', 'is', project_id]], ['code', 'sg_project_id'])
projectId = projectId['sg_project_id']

def getTypeAsset(name):
    return sg.find_one("Asset", [["code", "is", name]], ['sg_asset_type'])


if shot is None:
    print('-------------------------------------------------------------------------------------------------------')
    print(' NOTHING TO EXPORT')
    print('-------------------------------------------------------------------------------------------------------')
else:

    dir_log = os.path.join(path, locale, 'data', 'log', str(shot['sg_sequence']['name']))
    if not os.path.exists(dir_log):
        os.makedirs(dir_log)

    path_log = os.path.join(dir_log, '{0}.log'.format(shot['code']))
    logging.basicConfig(filename=path_log, level=logging.DEBUG, format='%(asctime)s: %(levelname)s %(message)s')
    logger = logging.getLogger(__name__)

    print('-------------------------------------------------------------------------------------------------------')
    print(' COLLECTING DATA TO START EXPORT')
    print('-------------------------------------------------------------------------------------------------------')
    print(' FILE: {0}'.format(shot['sg_filename']))
    print(' VERSION: {0}'.format(shot['sg_file_version']))
    print(' SC/SHOT: {0}/{1}'.format(shot['sg_sequence']['name'], shot['code']))
    print(' PROJECT PATH: {0}'.format(path))
    roots = json.loads(shot['sg_root'])
    print(' MESH EXPORT: {0}'.format(len(roots)))

    folder_exists = os.path.join(path, locale, 'cache', 'alembic', 'Animation', str(shot['sg_sequence']['name']), str(shot['code']))

    if not os.path.exists(folder_exists):
        print('-------------------------------------------------------------------------------------------------------')
        print(' CREATE FOLDER {0}'.format(shot['code']))
        print('-------------------------------------------------------------------------------------------------------')
        os.makedirs(folder_exists)
        logger.info(' * CREATE FOLDER {0}'.format(shot['code']))

    print('-------------------------------------------------------------------------------------------------------')
    print(' INITIALIZE MAYA')
    print('-------------------------------------------------------------------------------------------------------')

    file = os.path.join(path, locale, 'users', str(shot['sg_sequence']['name']), str(shot['code']), 'Animation', '{0}.{1}.ma'.format(shot['sg_filename'], shot['sg_file_version']))

    alembicArgs = [
        '-uvWrite',
        '-stripNamespaces',
        '-worldSpace',
        '-writeVisibility',
    ]

    maya.standalone.initialize()
    cmds.loadPlugin('AbcExport.mll')
    cmds.disableIncorrectNameWarning()

    cmds.workspace(directory=path)
    cmds.file(file, open=True, force=True, loadReferenceDepth='all', prompt=False)
    version = cmds.about(v=True)
    print('-------------------------------------------------------------------------------------------------------')
    print(' MAYA {0}'.format(version))

    cleanups = ['cleanPlugins', 'cleanUnknowNodes', 'clearOthers']
    unknownNodes = cmds.ls(type="unknown")

    try:
        print('-------------------------------------------------------------------------------------------------------')
        print(' CLEANUP FILE UNKNOWPLUGUIN AND UNKNOWNODE')
        print('-------------------------------------------------------------------------------------------------------')

        for p in plugins:
            print('-> PLUGINS, {0}'.format(p))
            if cmds.pluginInfo(p, query=True, loaded=True):
                cmds.unloadPlugin(p, force=True)
                cmds.pluginInfo(p, edit=True, autoload=False)

        for item in unknownNodes:
            print('-> UNKNOW {0}'.format(item))
            if cmds.objExists(item):
                cmds.delete(item)

        print('-> OTHERS')
        try:
            cmds.unknownPlugin("Mayatomr", remove)
            cmds.lockNode('TurtleDefaultBakeLayer', lock=False)
            cmds.delete('TurtleDefaultBakeLayer')
            cmds.delete('_UNKNOWN_REF_NODE_')
        except:
            pass

        cmds.file(save=True, type="mayaAscii")

    except:
        print(' X Error cleanup unknowpluguin, unknownode')
        print('-------------------------------------------------------------------------------------------------------')
        pass

    print('\n\n STARTING PROCESS EXPORT ALEMBIC')
    print('-------------------------------------------------------------------------------------------------------\n\n')
    alembicArgs = ' '.join(alembicArgs)
    processed = 'wait'
    mbAlembicAata = {}

    for item in roots:
        explodeName = item['object'].split(':')
        itemName = explodeName[0].split(":")[0].split("_")[0]
        masterGroup = explodeName[1]
        mbAlembicAata[itemName] = []
    try:
        i = 0
        for root in roots:
            print(' EXPORTING {0}'.format(root['name'].upper()))
            print('-------------------------------------------------------------------------------------------------------')
            if root['exported']:
                taskName = root['object'].split(':')[0]
                taskName = taskName.split(":")[0].split("_")[0]
                getAsset = getTypeAsset(taskName)
                alembic_path = os.path.join(path, '02_prod', 'cache', 'alembic', 'Animation', str(shot['sg_sequence']['name']), str(shot['code']), str('{0}{1}{2}.abc'.format(projectId, taskName, i)))
                alembic_path = alembic_path.replace('\\', '/')

                lookdev_path = os.path.join(path, '02_prod', 'assets', getAsset['sg_asset_type'], taskName, 'LookDev', 'maya', str('{0}{1}.v001.ma'.format(projectId, taskName)))
                lookdev_path = lookdev_path.replace('\\', '/')

                abc_export_cmd = "-frameRange {start} {end} {args} -dataFormat ogawa -root {root} -file '{file}'".format(
                    start=shot['sg_cut_in'],
                    end=shot['sg_cut_out'],
                    args=alembicArgs,
                    root=root['root'],
                    file=alembic_path
                )
                try:
                    cmds.AbcExport(jobArg=abc_export_cmd)
                    print(' > Export complete')
                    roots[i]['processed'] = True
                    processed = 'success'
                    logger.info(' EXPORTING {0}{1}'.format(projectId, taskName.upper()))
                    mbAlembicAata[taskName].append({"id": str('{0}{1}{2}'.format(projectId, taskName, i)),
                                                    "filename": str('{0}{1}{2}.abc'.format(projectId, taskName, i)),
                                                    "shot": shot['code'],
                                                    "sc": shot['sg_sequence']['name'],
                                                    "alembic_path": alembic_path,
                                                    "master_group": masterGroup,
                                                    "reference_file": lookdev_path
                    })
                except Exception as e:
                    logger.error('Error {0}{1} -> {2}'.format(projectId, str(taskName), str(e)))
                    processed = 'error'
                    print(' * Export error, check the log file: %s' % str(path_log))
                print('-------------------------------------------------------------------------------------------------------')
            else:
                print(' ! Object not selected for export %s' % str(taskName))
                logger.warning(' ! Object not selected for export  %s' % str(taskName))
            i += 1
    except Exception as e:
        # logger.error('Error shot' % e)
        print(e)
        processed = 'error'
    print('UPDATING {0} SHOTGUN SERVER'.format(shot['code']))
    sg.update('Shot', shot['id'], {'sg_exported': 'False', 'sg_processed': processed, 'sg_root': json.dumps(roots), 'sg_mb_alembic_data': json.dumps(mbAlembicAata)})
    print(' * Success')
time.sleep(3)
