from PySide6.QtCore import QDir

from AppFile.Menu.exportMenu import AdvancedExportMenu
from AppFile.Utility import fileUtility, exportUtility
from AppFile.WorkArea.fileStructArea import *
from AppFile.WorkArea.previewArea import PreviewArea

APP_TITLE = 'CreatiView'


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class SingletonRootDir(QDir):
    def __init__(self, path=''):
        super().__init__(path)

    def setPath(self, path):
        super().setPath(path)


@singleton
class SingletonCurrentDir(QDir):
    def __init__(self, path=''):
        super().__init__(path)

    def setPath(self, path):
        super().setPath(path)


@singleton
class SingletonSysModel(QFileSystemModel):
    def __init__(self):
        super().__init__()


@singleton
class SingletonMainWin(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.setWindowTitle(APP_TITLE)

        # Singleton variable creation
        root_dir = SingletonRootDir('M:/download/test')
        current_dir = SingletonCurrentDir(root_dir.absolutePath())
        sys_model = SingletonSysModel()
        sys_model.setRootPath(QDir.currentPath())

        # Menu Bar
        menu_bar = self.menuBar()
        menu_bar_file_menu = menu_bar.addMenu('file')
        open_folder_action = menu_bar_file_menu.addAction('open folder')
        new_folder_action = menu_bar_file_menu.addAction('new folder')
        new_file_action = menu_bar_file_menu.addAction('new file')
        import_dir_action = menu_bar_file_menu.addAction('import folder')
        menu_bar_export_menu = menu_bar.addMenu('export')
        # quick_export_action = menu_bar_export_menu.addAction('quick export')
        advanced_export_action = menu_bar_export_menu.addAction('advanced export')

        # Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage('status message')

        # Signal Linkage
        open_folder_action.triggered.connect(fileUtility.open_folder)
        new_folder_action.triggered.connect(fileUtility.new_folder)
        new_file_action.triggered.connect(fileUtility.new_file)
        import_dir_action.triggered.connect(fileUtility.import_dir)
        #quick_export_action.triggered.connect(exportUtility.quick_export)
        advanced_export_action.triggered.connect(self.call_advanced_export)

        # Work Area Creation
        self.file_struct_area = FileStructArea()
        self.preview_area = PreviewArea()

        # Display Work Area
        left_right_split = QSplitter(Qt.Horizontal)
        left_right_split.addWidget(self.file_struct_area)
        left_right_split.addWidget(self.preview_area)
        left_right_split.setSizes([1,1])
        self.setCentralWidget(left_right_split)

    def delegate_root_dir_changed(self):
        self.file_struct_area.root_dir_changed()

    def delegate_current_dir_changed(self):
        self.file_struct_area.current_dir_changed()

    def call_advanced_export(self):
        AdvancedExportMenu().exec()
