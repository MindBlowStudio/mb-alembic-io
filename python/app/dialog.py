import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
import requests
import subprocess
import os
import time
import json

logger = sgtk.platform.get_logger(__name__)


def show_dialog(app_instance):
    app_instance.engine.show_dialog('MB Alembic IO', app_instance, AppDialog)


class AppDialog(QtGui.QWidget):
    def __init__(self):

        QtGui.QWidget.__init__(self)

        self.app = sgtk.platform.current_bundle()
        self.project_path = self.app.engine.tank.project_path

        self.data = []
        self.sequences = []
        self.sequence = {}

        self.tk = sgtk.sgtk_from_path(self.project_path)
        self.ctx = self.tk.context_from_path(self.project_path)
        self.user_data = sgtk.util.get_current_user(self.app.sgtk)

        self.shotgun_connection = sgtk.platform.current_bundle().shotgun
        QtCore.QCoreApplication.processEvents()

        user_info = self.shotgun_connection.find_one(
            "HumanUser",
            [["login", "is", self.user_data['login']]],
            ["entity_hash", "permission_rule_set"],
        )

        try:
            permission = user_info["permission_rule_set"]
            if "Admin" not in permission['name']:
                QtGui.QMessageBox.warning(None, "Not permission", "Only administrators can access this model!", QtGui.QMessageBox.Ok)
                QtCore.QTimer.singleShot(0, self.close)
                return
            self.ui = Ui_Dialog()
            self.ui.storage(self)
            self.ui.setupUi(self)

            self.ui.loader('load')
            self.loadSequences()
            self.ui.buttonExport.setDisabled(True)
            self.ui.searchField.setDisabled(True)

            self.ui.buttonExport.clicked.connect(self.export)

        except Exception as e:
            logger.debug(e)

    def loadSequences(self):

        filter = [['project.Project.id', 'is', self.ctx.project['id']]]
        self.sequences = self.shotgun_connection.find('Sequence', filter, ['id', 'code'])

        self.ui.selectSequences.addItem('Sequence')
        for sec in self.sequences:
            self.ui.selectSequences.addItem(sec['code'])
        QtCore.QCoreApplication.processEvents()
        self.ui.loader('empty')

        self.ui.selectSequences.currentIndexChanged.connect(self.setSequence)
        self.ui.selectLocale.currentIndexChanged.connect(self.resetSequence)

    def resetSequence(self):
        QtCore.QCoreApplication.processEvents()
        self.data = []
        self.ui.selectSequences.setCurrentIndex(0)

    def setSequence(self, index):
        QtCore.QCoreApplication.processEvents()
        if index > 0:
            self.sequence = self.sequences[(index - 1)]
            self.dataLoad()
        else:
            self.ui.loader('empty')

    def dataLoad(self):
        self.clearFiles()
        self.ui.loader('load')
        self.data = []
        QtCore.QCoreApplication.processEvents()
        self.data = self.shotgun_connection.find(
            'Shot',
            [
                ['project.Project.id', 'is', self.ctx.project['id']],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': self.sequence['id']}],
                ['sg_root', 'is_not', None]
            ],
            ['code', 'project', 'sg_sequence', 'image', 'sg_status_list', 'sg_root', 'sg_file_version', 'sg_file_created', 'sg_file_updated', 'sg_filename', 'sg_processed', 'sg_exported']
        )

        self.data.sort(key=lambda o: o['code'])

        if len(self.data) > 0:
            self.ui.loader('list')
            self.addItems()
            self.ui.buttonExport.setDisabled(False)
            self.ui.buttonReload.setDisabled(False)
            self.ui.searchField.setDisabled(False)
        else:
            self.ui.loader('no-items')
            self.ui.buttonExport.setDisabled(True)
            self.ui.searchField.setDisabled(True)
            self.ui.buttonReload.setDisabled(True)

    def getUpdateData(self):
        data = self.shotgun_connection.find(
            'Shot',
            [
                ['project.Project.id', 'is', self.ctx.project['id']],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': self.sequence['id']}],
                ['sg_root', 'is_not', None]
            ],
            ['code', 'sg_processed', 'sg_exported']
        )

        return data

    def addItems(self):
        i = 0

        for item in self.data:
            if item['image']:
                item['image_url'] = requests.get(item['image']).content
            shotItem = self.ui.item(item)
            self.ui.formLayout.setWidget(i, QtGui.QFormLayout.FieldRole, shotItem)
            i += 1
        QtCore.QCoreApplication.processEvents()
        self.ui.searchField.setDisabled(False)

    def clearFiles(self):
        if self.ui.formLayout.count() > 0:
            for i in range(self.ui.formLayout.count()):
                self.ui.formLayout.itemAt(i).widget().deleteLater()
                QtCore.QCoreApplication.processEvents()

    def export(self):

        total = len(filter(lambda f: f['sg_exported'] == 'True', self.data))
        data = filter(lambda s: s['sg_exported'] == 'True', self.data)

        if total > 0:
            self.ui.buttonExport.setDisabled(True)
            loaded = 0
            path = os.path.dirname(__file__)
            file = os.path.join(path, "export.py")
            self.ui.progress.setVisible(True)
            for i in range(self.ui.formLayout.count()):
                self.ui.formLayout.itemAt(i).widget().setDisabled(True)
                self.ui.formLayout.itemAt(i).widget().findChild(QtGui.QLabel, 'status').setPixmap(QtGui.QPixmap(self.ui.loadImage("alembic")))

            while loaded < total:
                loaded += 1
                pct = ((loaded * 100) / total)
                self.ui.progress.setFormat("{shot} EXPORTING %p%".format(shot=data[(loaded - 1)]['code']))
                self.ui.progress.setProperty("value", pct)
                cmd = "start /w %MAYA_PYTHON% {file} {shot} {project} {path} {locale}".format(file=file, shot=data[(loaded - 1)]['id'], project=self.ctx.project['id'], path=str(self.project_path.replace(' ', '-')), locale=str(self.ui.selectLocale.currentText()))
                os.system(cmd)
                QtCore.QCoreApplication.processEvents()

            self.ui.progress.setVisible(False)
            self.ui.progress.setProperty("value", 0)
            self.ui.progress.setFormat("")

            listUpdate = self.getUpdateData()

            x = 0
            for up in listUpdate:
                self.ui.formLayout.itemAt(x).widget().setDisabled(False)
                self.ui.formLayout.itemAt(x).widget().findChild(QtGui.QCheckBox, 'export').setChecked(False)
                self.ui.formLayout.itemAt(x).widget().findChild(QtGui.QLabel, 'status').setPixmap(QtGui.QPixmap(self.ui.loadImage(up['sg_processed'])))
                x += 1
            self.ui.buttonExport.setDisabled(False)
        else:
            QtGui.QMessageBox.information(None, "Alert", "Nothing shot selected", QtGui.QMessageBox.Ok)
