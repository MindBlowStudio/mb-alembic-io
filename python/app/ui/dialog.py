import os
import sgtk
from tank.platform.qt import QtCore, QtGui
import datetime
import json
import glob
import time

logger = sgtk.platform.get_logger(__name__)


class Ui_Dialog(object):

    def storage(self, parent):
        self.parent = parent

    def setupUi(self, Main):
        logger.info(object)
        self.bundle = sgtk.platform.current_bundle()
        self.project_path = self.bundle.engine.tank.project_path
        self.root_path = os.path.dirname(__file__)

        self.app = sgtk.platform.current_bundle()
        self.tk = sgtk.sgtk_from_path(self.project_path)
        self.ctx = self.tk.context_from_path(self.project_path)
        self.connection = sgtk.platform.current_bundle().shotgun

        Main.setObjectName("Main")
        Main.setWindowModality(QtCore.Qt.NonModal)
        Main.setEnabled(True)
        Main.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        Main.setWindowTitle("Zombie Alembic IO")

        self.main = Main
        self.mainLayout = QtGui.QVBoxLayout(Main)
        self.mainLayout.setObjectName("mainLayout")
        self.layoutHeader = QtGui.QHBoxLayout()
        self.layoutHeader.setContentsMargins(0, 0, 0, 0)
        self.layoutHeader.setObjectName("layoutHeader")

        self.selectLocale = QtGui.QComboBox(Main)
        self.selectLocale.setObjectName("selectLocale")
        self.selectLocale.addItems(['06_prod_anim', '02_prod'])
        self.layoutHeader.addWidget(self.selectLocale)

        self.selectSequences = QtGui.QComboBox(Main)
        self.selectSequences.setObjectName("selectSequences")
        self.layoutHeader.addWidget(self.selectSequences)

        self.searchField = QtGui.QLineEdit(Main)
        self.searchField.setObjectName("searchField")
        self.layoutHeader.addWidget(self.searchField)
        self.search = QtGui.QLabel(Main)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search.sizePolicy().hasHeightForWidth())
        self.search.setSizePolicy(sizePolicy)
        self.search.setMinimumSize(QtCore.QSize(20, 20))
        self.search.setText("")
        self.search.setPixmap(QtGui.QPixmap(self.loadImage("search_small")))
        self.search.setObjectName("search")
        self.layoutHeader.addWidget(self.search)

        self.mainLayout.addLayout(self.layoutHeader)

        self.progress = QtGui.QProgressBar(Main)
        self.progress.setProperty("value", 0)
        self.progress.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.progress.setOrientation(QtCore.Qt.Horizontal)
        self.progress.setInvertedAppearance(False)
        self.progress.setVisible(False)
        self.progress.setTextDirection(QtGui.QProgressBar.BottomToTop)
        self.progress.setObjectName("progress")
        self.progress.setFormat("")
        self.mainLayout.addWidget(self.progress)

        lineUp = QtGui.QFrame(Main)
        lineUp.setFrameShape(QtGui.QFrame.HLine)
        lineUp.setFrameShadow(QtGui.QFrame.Sunken)
        lineUp.setObjectName("lineUp")
        self.mainLayout.addWidget(lineUp)
        self.displayLayout = QtGui.QVBoxLayout()
        self.displayLayout.setContentsMargins(0, 0, -1, 0)
        self.displayLayout.setSpacing(0)
        self.displayLayout.setObjectName("displayLayout")
        self.display = QtGui.QLabel(Main)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.display.sizePolicy().hasHeightForWidth())
        self.display.setSizePolicy(sizePolicy)
        self.display.setAutoFillBackground(False)
        self.display.setStyleSheet("background-color:#2b2b2b;opacity:.2")
        self.display.setText("")
        self.display.setTextFormat(QtCore.Qt.PlainText)
        self.display.setScaledContents(False)
        self.display.setAlignment(QtCore.Qt.AlignCenter)
        self.display.setWordWrap(False)
        self.display.setIndent(0)
        self.display.setOpenExternalLinks(False)
        self.display.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.display.setObjectName("display")
        self.displayLayout.addWidget(self.display)

        self.scrollList = QtGui.QScrollArea(Main)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollList.sizePolicy().hasHeightForWidth())
        self.scrollList.setSizePolicy(sizePolicy)
        self.scrollList.setMinimumSize(QtCore.QSize(0, 300))
        self.scrollList.setSizeIncrement(QtCore.QSize(0, 300))
        self.scrollList.setWidgetResizable(True)
        self.scrollList.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.scrollList.setObjectName("scrollList")

        self.shotList = QtGui.QWidget()
        self.shotList.setGeometry(QtCore.QRect(0, 0, 557, 298))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.shotList.sizePolicy().hasHeightForWidth())
        self.shotList.setSizePolicy(sizePolicy)
        self.shotList.setObjectName("shotList")
        self.shotLayout = QtGui.QVBoxLayout(self.shotList)
        self.shotLayout.setContentsMargins(0, 0, 0, 0)
        self.shotLayout.setSpacing(0)
        self.shotLayout.setObjectName("shotLayout")

        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtGui.QFormLayout.WrapAllRows)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setObjectName("formLayout")

        self.shotLayout.addLayout(self.formLayout)
        self.scrollList.setWidget(self.shotList)
        self.displayLayout.addWidget(self.scrollList)

        self.mainLayout.addLayout(self.displayLayout)

        lineDown = QtGui.QFrame(Main)
        lineDown.setFrameShape(QtGui.QFrame.HLine)
        lineDown.setFrameShadow(QtGui.QFrame.Sunken)
        lineDown.setObjectName("lineDown")
        self.mainLayout.addWidget(lineDown)

        self.actionlayout = QtGui.QHBoxLayout()
        self.actionlayout.setContentsMargins(-1, -1, -1, 0)
        self.actionlayout.setObjectName("actionlayout")
        self.buttonExport = QtGui.QPushButton(Main)
        self.buttonExport.setCheckable(False)
        self.buttonExport.setAutoRepeat(False)
        self.buttonExport.setObjectName("buttonExport")
        self.actionlayout.addWidget(self.buttonExport)
        self.mainLayout.addLayout(self.actionlayout)

        self.retranslateUi(Main)
        QtCore.QMetaObject.connectSlotsByName(Main)

    def retranslateUi(self, Main):
        _translate = QtCore.QCoreApplication.translate
        self.searchField.setPlaceholderText(_translate("Main", "Searching for..."))
        self.buttonExport.setText(_translate("Main", "EXPORT ALEMBIC"))

    def item(self, data):
        try:
            item = QtGui.QWidget(self.shotList)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(item.sizePolicy().hasHeightForWidth())
            item.setSizePolicy(sizePolicy)
            item.setMinimumSize(QtCore.QSize(0, 100))
            item.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            item.setAutoFillBackground(True)
            item.setObjectName("item")
            itemLayout = QtGui.QHBoxLayout(item)
            itemLayout.setSpacing(6)
            itemLayout.setObjectName("itemLayout")

            export = QtGui.QCheckBox(item)
            export.setText("")

            if data['sg_exported'] == 'True' and data['sg_exported'] is not None:
                export.setChecked(True)
            else:
                export.setChecked(False)

            export.setIconSize(QtCore.QSize(20, 20))
            export.setObjectName("export")
            itemLayout.addWidget(export)

            thumb = QtGui.QLabel(item)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(thumb.sizePolicy().hasHeightForWidth())
            thumb.setSizePolicy(sizePolicy)
            thumb.setMinimumSize(QtCore.QSize(120, 80))
            thumb.setMaximumSize(QtCore.QSize(120, 80))
            thumb.setAutoFillBackground(False)
            thumb.setStyleSheet("background-color:black;")
            thumb.setText("")

            try:
                if data['image']:
                    image = QtGui.QImage()
                    image.loadFromData(data['image_url'])
                    pixmap = QtGui.QPixmap(image)
                    thumb.setPixmap(pixmap)
                else:
                    thumb.setPixmap(QtGui.QPixmap(self.loadImage("thumb")))
            except:
                thumb.setPixmap(QtGui.QPixmap(self.loadImage("thumb")))

            thumb.setScaledContents(True)
            thumb.setObjectName("thumb")
            itemLayout.addWidget(thumb)
            info = QtGui.QLabel(item)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(info.sizePolicy().hasHeightForWidth())
            info.setSizePolicy(sizePolicy)
            info.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            info.setObjectName("info")
            itemLayout.addWidget(info)
            line = QtGui.QFrame(item)
            line.setFrameShape(QtGui.QFrame.VLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            line.setObjectName("line")
            itemLayout.addWidget(line)
            FileVersion = QtGui.QWidget(item)
            FileVersion.setMinimumSize(QtCore.QSize(100, 0))
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(FileVersion.sizePolicy().hasHeightForWidth())
            FileVersion.setSizePolicy(sizePolicy)
            FileVersion.setObjectName("FileVersion")
            layoutFileVersion = QtGui.QVBoxLayout(FileVersion)
            layoutFileVersion.setContentsMargins(0, 0, 0, 0)
            layoutFileVersion.setSpacing(0)
            layoutFileVersion.setObjectName("layoutFileVersion")
            titleFileVersion = QtGui.QLabel(FileVersion)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(titleFileVersion.sizePolicy().hasHeightForWidth())
            titleFileVersion.setSizePolicy(sizePolicy)
            titleFileVersion.setObjectName("titleFileVersion")
            layoutFileVersion.addWidget(titleFileVersion)
            listFiles = QtGui.QComboBox(FileVersion)
            listFiles.setObjectName("listFiles")
            layoutFileVersion.addWidget(listFiles)
            listVersions = QtGui.QComboBox(FileVersion)
            listVersions.setObjectName("listVersions")
            layoutFileVersion.addWidget(listVersions)
            itemLayout.addWidget(FileVersion)

            objectList = QtGui.QTreeWidget(item)
            objectList.setMinimumSize(QtCore.QSize(100, 0))
            objectList.setAutoScrollMargin(16)
            objectList.setProperty("showDropIndicator", True)
            objectList.setAlternatingRowColors(True)
            objectList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
            objectList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            objectList.setIndentation(0)
            objectList.setObjectName("objectList")
            itemLayout.addWidget(objectList)
            status = QtGui.QLabel(item)
            status.setText("")
            status.setPixmap(QtGui.QPixmap(self.loadImage(data['sg_processed'])))
            status.setIndent(0)
            status.setOpenExternalLinks(False)
            status.setObjectName("status")
            itemLayout.addWidget(status)

            create = '---'
            update = '---'
            objects = json.loads(data['sg_root'])

            if data['sg_file_created']:
                create = datetime.datetime.strptime(data['sg_file_created'], '%Y-%m-%d').strftime('%d/%m/%Y')

            if data['sg_file_updated']:
                update = datetime.datetime.strptime(data['sg_file_updated'], '%Y-%m-%d').strftime('%d/%m/%Y')

            info.setText("<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">{shot}</span><span style=\" font-size:9pt; font-weight:600;\"><br/></span><span style=\" font-size:9pt;\">Created: {created}<br/>updated: {updated}<br/>Objects: {root}</span></p></body></html>".format(
                shot=data['code'],
                created=create,
                updated=update,
                root=len(objects)
            ))

            for obj in objects:
                objectItem = QtGui.QTreeWidgetItem(objectList)
                objectItem.setData(0, QtCore.Qt.UserRole, {'id': data['id'], 'item': obj, 'data': objects})
                objectItem.setText(0, obj['name'])
                objectItem.setSelected(obj['exported'])

            FileVersions = self.getFileVersions(data['sg_sequence']['name'], data['code'])
            list_files = FileVersions['files']
            list_versions = FileVersions['versions']
            indexFile = list_files.index(data['sg_filename'])
            list_versions = list_versions[indexFile][data['sg_filename']]
            indexVersion = list_versions.index(data['sg_file_version'])

            listFiles.addItems(list_files)
            listFiles.setCurrentIndex(indexFile)

            listVersions.addItems(list_versions)
            listVersions.setCurrentIndex(indexVersion)

            if len(list_files) <= 1:
                listFiles.setDisabled(True)

            if len(list_versions) <= 1:
                listVersions.setDisabled(True)

            objectList.itemClicked.connect(self.setObject)

            listFiles.currentIndexChanged.connect(lambda f: self.setFilename(f, data['id'], FileVersions, listVersions))
            listVersions.currentIndexChanged.connect(lambda f: self.setFileversion(f, data['id'], listVersions))
            export.stateChanged.connect(lambda e: self.setExported(e, data['id']))

            titleFileVersion.setText("<html><head/><body><p><span style=\" font-weight:600;\">File/Version</span></p></body></html>")
            objectList.headerItem().setText(0, "Meshs")
            __sortingEnabled = objectList.isSortingEnabled()
            objectList.setSortingEnabled(False)
            objectList.setSortingEnabled(__sortingEnabled)
        except Exception as e:
            logger.info(e)
            pass
        return item

    def setFilename(self, index, id, data, target):
        target.clear()
        items = data['versions'][index].values()[0]
        name = data['files'][index]
        last = items[-1:][0]
        indexVersion = items.index(last)
        target.addItems(items)
        target.setCurrentIndex(indexVersion)

        if len(items) > 1:
            target.setDisabled(False)
        else:
            target.setDisabled(True)

        self.update(id, {'sg_filename': name, 'sg_file_version': last})
        self.updateData(id, 'sg_filename', name)
        self.updateData(id, 'sg_file_version', last)

    def setObject(self, it, col):
        data = it.data(0, QtCore.Qt.UserRole)
        item = data['item']
        index = next(i for i, x in enumerate(data['data']) if x['name'] == item['name'])
        data['data'][index]['exported'] = it.isSelected()
        self.update(data['id'], {'sg_root': json.dumps(data['data'])})
        self.updateData(data['id'], 'sg_root', json.dumps(data['data']))
        logger.info(json.dumps(data['data']))
        it.setData(0, QtCoreRole, data)

    def setExported(self, checked, id):
        _value = 'False'
        if checked > 0:
            _value = 'True'
        self.update(id, {'sg_exported': _value})
        self.updateData(id, 'sg_exported', _value)

    def setFileversion(self, index, id, target):
        version = target.currentText()
        self.update(id, {'sg_file_version': version})
        self.updateData(id, 'sg_file_version', version)

    def loadImage(self, name):
        return os.path.join(self.root_path, "../../../resources", "{image}.png".format(image=name))

    def loader(self, name):
        QtCore.QCoreApplication.processEvents()

        if name == 'load':
            self.main.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        else:
            self.main.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        if name == 'list':
            self.display.setVisible(False)
            self.scrollList.setVisible(True)
        else:
            self.display.setVisible(True)
            self.scrollList.setVisible(False)
            self.display.setPixmap(QtGui.QPixmap(os.path.join(self.root_path, "../../../resources", "{name}.png".format(name=name))))

    def update(self, id, data):
        QtCore.QCoreApplication.processEvents()
        self.connection.update('Shot', id, data)

    def getFileVersions(self, sc, shot):
        locale = self.selectLocale.currentText()
        path = os.path.join(self.project_path, locale, 'users', sc, shot, 'Animation')
        logger.info(path)
        try:
            if os.path.exists(path):
                files = glob.glob("{path}\\*.ma".format(path=path))

                groupFiles = []
                for file in files:
                    name = file.split('\\')[-1:][0].split('.')[0]
                    groupFiles.append(name)
                groupFiles = list(dict.fromkeys(groupFiles))

                result = {shot: {}}
                result[shot]['files'] = []
                result[shot]['versions'] = []
                for x in groupFiles:
                    versions = {x: []}
                    for y in files:
                        if x in y:
                            version = y.split('\\')[-1:][0].split('.')[1]
                            version = version[:8]
                            versions[x].append(version)
                    result[shot]['versions'].append(versions)
                    result[shot]['files'].append(x)
                return result[shot]
            else:
                return []
        except:
            return []

    def updateData(self, id, attr, value):
        index = next(i for i, x in enumerate(self.parent.data) if x['id'] == id)
        self.parent.data[index][attr] = value
