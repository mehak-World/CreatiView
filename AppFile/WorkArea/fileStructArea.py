import os
from enum import Enum
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from AppFile import singleton
from AppFile.Utility import fileUtility

PathItemType = Enum('PathItemType', ['FOLDER', 'CONTEXT_FOLDER', 'CONFIG_FILE', 'TEXT_FILE', 'OTHER_FILE'])


class FileStructArea(QWidget):
    def __init__(self):
        super().__init__()

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.tree_view = TreeView()

        button_new_folder = QPushButton('new folder', self)
        button_new_folder.pressed.connect(fileUtility.new_folder)
        button_new_file = QPushButton('new file', self)
        button_new_file.pressed.connect(fileUtility.new_file)
        button_import_dir = QPushButton('import folder', self)
        button_import_dir.pressed.connect(fileUtility.import_dir)
        button_rename = QPushButton('rename', self)
        button_rename.pressed.connect(lambda: fileUtility.rename(self.tree_view.current_file_path))
        button_remove = QPushButton('delete', self)
        button_remove.pressed.connect(lambda: fileUtility.remove(self.tree_view.current_file_path))

        h_layout.addWidget(button_new_folder)
        h_layout.addWidget(button_new_file)
        h_layout.addWidget(button_import_dir)
        h_layout.addWidget(button_rename)
        h_layout.addWidget(button_remove)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.tree_view)

        # Display area
        self.setLayout(v_layout)

    def root_dir_changed(self):
        self.tree_view.update_root_index()

    def current_dir_changed(self):
        pass


class TreeView(QTreeView):
    def __init__(self):
        super().__init__()

        # Use custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Singleton Variable
        root_dir = singleton.SingletonRootDir()
        current_dir = singleton.SingletonCurrentDir()
        sys_model = singleton.SingletonSysModel()

        # Variables
        self.current_file_path = current_dir.absolutePath()
        self.setDragEnabled(True)

        if sys_model:
            self.setModel(sys_model)
        else:
            pass  # Error setting up model

        if root_dir:
            self.update_root_index()

        # Signal Linkage
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.pressed.connect(self.update_current_index)
        self.doubleClicked.connect(lambda: fileUtility.open_file(self.current_file_path))

    def update_root_index(self):
        sys_model = singleton.SingletonSysModel()
        root_dir = singleton.SingletonRootDir()
        self.setRootIndex(sys_model.index(root_dir.absolutePath()))

    def update_current_index(self, index):
        current_dir = singleton.SingletonCurrentDir()
        sys_model = singleton.SingletonSysModel()
        # Keep a path and directory, which is the same if path is directory
        self.current_file_path = sys_model.filePath(index)
        if os.path.isdir(self.current_file_path):
            current_dir.setPath(self.current_file_path)
        else:
            parent_path = os.path.dirname(self.current_file_path)
            current_dir.setPath(parent_path)

    # Contex menu
    def open_context_menu(self, pos):
        menu = None

        if os.path.isdir(self.current_file_path):
            if fileUtility.is_path_context_folder(self.current_file_path):
                menu = self.generate_context_menu(PathItemType.CONTEXT_FOLDER)
            else:
                menu = self.generate_context_menu(PathItemType.FOLDER)
        else:
            if self.current_file_path.endswith('.context.ini'):
                menu = self.generate_context_menu(PathItemType.CONFIG_FILE)
            elif self.current_file_path.endswith('.txt'):
                menu = self.generate_context_menu(PathItemType.TEXT_FILE)
            else:
                menu = self.generate_context_menu(PathItemType.OTHER_FILE)

        menu.exec(self.mapToGlobal(pos))

    def generate_context_menu(self, path_item_type):
        main_win = singleton.SingletonMainWin()

        context_menu = QMenu(main_win)

        if path_item_type == PathItemType.FOLDER or path_item_type == PathItemType.CONTEXT_FOLDER:
            new_folder_action = context_menu.addAction('new folder')
            new_folder_action.triggered.connect(fileUtility.new_folder)
            new_context_folder_action = context_menu.addAction('new context folder')
            new_context_folder_action.triggered.connect(fileUtility.new_context_folder)

        if path_item_type == PathItemType.FOLDER:
            convert_to_context_folder_action = context_menu.addAction('convert to context folder')
            convert_to_context_folder_action.triggered.connect(
                lambda: fileUtility.create_config_file_at_path(self.current_file_path))

        if path_item_type == PathItemType.FOLDER or path_item_type == PathItemType.CONTEXT_FOLDER:
            new_file_action = context_menu.addAction('new file')
            new_file_action.triggered.connect(fileUtility.new_file)
            import_dir_action = context_menu.addAction('import folder')
            import_dir_action.triggered.connect(fileUtility.import_dir)

        if path_item_type == PathItemType.TEXT_FILE or path_item_type == PathItemType.CONFIG_FILE:
            open_file_action = context_menu.addAction('edit')
            open_file_action.triggered.connect(lambda: fileUtility.open_file(self.current_file_path))

        if not path_item_type == PathItemType.CONFIG_FILE:
            rename_action = context_menu.addAction('rename')
            rename_action.triggered.connect(lambda: fileUtility.rename(self.current_file_path))
            move_to_action = context_menu.addAction('move')
            move_to_action.triggered.connect(lambda: fileUtility.move_to(self.current_file_path))

        remove_action = context_menu.addAction('delete')
        remove_action.triggered.connect(lambda: fileUtility.remove(self.current_file_path))

        return context_menu
