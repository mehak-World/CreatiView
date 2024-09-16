import os.path
from enum import Enum
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QGroupBox, QLabel, QTextEdit, QHBoxLayout, QComboBox, \
    QLineEdit, QRadioButton, QCheckBox, QFileDialog
from AppFile import singleton
from AppFile.Utility import fileUtility
from AppFile.Utility.exportUtility import Exporter

MetaRule = Enum('MetaRule', ['NONE', 'NOTES', 'ALL'])


class AdvancedExportMenu(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Advanced Export')

        self.current_dir = singleton.SingletonCurrentDir()
        self.root_dir = singleton.SingletonRootDir()

        self.source_path = self.current_dir.absolutePath()
        self.dest_path = os.path.dirname(self.root_dir.absolutePath())
        self.file_name = 'export_' + QDateTime.currentDateTime().toString('MM_dd_HHmm') + '.txt'
        self.meta_rule = MetaRule.NONE
        self.filter_rule = ''

        directory_frame = QGroupBox('Directory')
        ordering_frame = QGroupBox('Ordering')
        content_frame = QGroupBox('Content')
        filer_frame = QGroupBox('Filter rule')

        # Directory Frame
        v_directory = QVBoxLayout()
        v_directory.addWidget(QLabel('Source directory'))
        v_directory_h1 = QHBoxLayout()
        self.source_path_label = QLabel('Exporting from path: %s' % self.source_path)
        self.source_path_option = QComboBox()
        self.source_path_option.addItems(['current directory', 'root directory', 'custom'])
        self.source_path_option.currentIndexChanged.connect(self.source_path_option_changed)
        self.source_path_button = QPushButton('Choose')
        self.source_path_button.clicked.connect(self.call_custom_source_path)
        self.source_path_button.setEnabled(False)
        v_directory_h1.addWidget(self.source_path_label)
        v_directory_h1.addWidget(self.source_path_option)
        v_directory_h1.addWidget(self.source_path_button)
        v_directory.addLayout(v_directory_h1)
        v_directory.addWidget(QLabel('Destination directory'))
        v_directory_h2 = QHBoxLayout()
        self.dest_path_label = QLabel('Exporting to path: %s' % self.dest_path)
        dest_dir_button = QPushButton('Choose')
        dest_dir_button.clicked.connect(self.call_custom_dest_path)
        v_directory_h2.addWidget(self.dest_path_label)
        v_directory_h2.addWidget(dest_dir_button)
        v_directory.addLayout(v_directory_h2)
        v_directory.addWidget(QLabel('File Name'))
        self.file_name_edit = QLineEdit()
        self.file_name_edit.setText(self.file_name)
        self.file_name_edit.editingFinished.connect(self.validate_file_name)
        v_directory.addWidget(self.file_name_edit)
        directory_frame.setLayout(v_directory)

        # ordering Frame
        v_ordering = QVBoxLayout()
        v_ordering_h1 = QHBoxLayout()
        v_ordering_h1.addWidget(QLabel('Priority'))
        self.priority_option = QComboBox()
        self.priority_option.addItems(['priority_1', 'priority_2', 'priority_3'])
        self.radio_accend = QRadioButton('Accending')
        self.radio_decend = QRadioButton('Decending')
        v_ordering_h1.addWidget(self.priority_option)
        v_ordering_h1.addWidget(self.radio_accend)
        v_ordering_h1.addWidget(self.radio_decend)
        v_ordering.addLayout(v_ordering_h1)
        self.file_first_box = QCheckBox('Include files before directories')
        v_ordering.addWidget(self.file_first_box)
        ordering_frame.setLayout(v_ordering)

        # Content Frame
        v_content = QVBoxLayout()
        v_content.addWidget(QLabel('Include file meta information in export:'))
        self.meta_rule_option = QComboBox()
        self.meta_rule_option.addItems(['none', 'notes only', 'full metadata'])
        self.meta_rule_option.currentIndexChanged.connect(self.meta_rule_option_changed)
        v_content.addWidget(self.meta_rule_option)
        content_frame.setLayout(v_content)

        # Filter Rule Frame
        v_filter = QVBoxLayout()
        self.filter_rule_edit = QLineEdit()
        self.filter_rule_edit.textChanged.connect(self.set_filter_rule)
        v_filter.addWidget(self.filter_rule_edit)
        filer_frame.setLayout(v_filter)

        # Buttons
        h_button = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)
        h_button.addWidget(cancel_button)
        export_button = QPushButton('Export')
        export_button.clicked.connect(self.call_export)
        h_button.addWidget(export_button)

        # Display Frame
        v_layout = QVBoxLayout()
        v_layout.addWidget(directory_frame)
        # v_layout.addWidget(ordering_frame)
        # v_layout.addWidget(content_frame)
        v_layout.addWidget(filer_frame)
        v_layout.addLayout(h_button)
        self.setLayout(v_layout)

    # Function Definition
    def source_path_option_changed(self):
        index = self.source_path_option.currentIndex()
        if(index == 0):  # current dir
                self.source_path = self.current_dir.absolutePath()
                self.source_path_button.setEnabled(False)
        elif(index == 1):  # root dir
                self.source_path = self.root_dir.absolutePath()
                self.source_path_button.setEnabled(False)
        elif(index == 2):  # custom
                self.source_path_button.setEnabled(True)

        self.source_path_label.setText('Exporting from path: %s' % self.source_path)

    def call_custom_source_path(self):
        file_dialog = QFileDialog()
        path = file_dialog.getExistingDirectory(self, 'source directory', self.root_dir.absolutePath())

        if path:
            self.source_path = path
            self.source_path_label.setText('Exporting from path: %s' % self.source_path)

    def call_custom_dest_path(self):
        file_dialog = QFileDialog()
        path = file_dialog.getExistingDirectory(self, 'destination directory', self.dest_path)

        if path:
            self.dest_path = path
            self.dest_path_label.setText('Exporting to path: %s' % self.dest_path)

    def validate_file_name(self):
        file_name = self.file_name_edit.text()
        file_name = fileUtility.file_name_in_txt(file_name)
        self.file_name = file_name
        self.file_name_edit.setText(file_name)

    def meta_rule_option_changed(self):
        index = self.meta_rule_option.currentIndex()
        if(index == 0):
                self.meta_rule = MetaRule.NONE
        elif(index == 1):
                self.meta_rule = MetaRule.NOTES
        elif(index == 2):
                self.meta_rule = MetaRule.ALL

    def set_filter_rule(self):
        self.filter_rule = self.filter_rule_edit.text()
        print(self.filter_rule)

    def call_export(self):
        if self.filter_rule:
            filter_list = self.filter_rule.split(',')
        else:
            filter_list = []
        Exporter(self.source_path, os.path.join(self.dest_path, self.file_name), filter_list).export()
        self.close()