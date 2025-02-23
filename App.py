import ctypes
import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from common import *
from ModManager import *
from DatabaseManager import *
from qt_classes.TerminalOutputWidget import TerminalOutputWidget

TITLE_FONT = QtGui.QFont('Consolas', 25)
BODY_FONT = QtGui.QFont('Consolas', 15)
BUTTON_FONT = QtGui.QFont('Consolas', 12)


def create_label(text, font):
    label = QLabel(text)
    label.setFont(font)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def create_list_element(row):
    global checkbox_list
    hbox = QHBoxLayout()
    mod_name = row["mod_name"]
    label = QLabel(mod_name)
    label.setFont(BODY_FONT)
    label.setStyleSheet("""
    QLabel {
        padding: 10px;
                        margin-left: 5px;
                        background-color: transparent;
    }
    """)
    checkbox = QCheckBox()
    checkbox.setStyleSheet("""
    QCheckBox {
        margin-right: 5px;
                           background-color: transparent;
    }
    """)
    if row["enabled"]:
        checkbox.setChecked(True)
    else:
        checkbox.setChecked(False)
    checkbox.stateChanged.connect(
        lambda state, param="mod_name": on_checkbox_state_changed(state, mod_name))
    checkbox_list.append(checkbox)
    hbox.addWidget(label)
    hbox.addStretch()
    hbox.addWidget(checkbox)
    return hbox


def create_line(height=2):
    line = QLabel()
    line.setFixedHeight(height)
    line.setStyleSheet("background-color: grey;")
    return line

def create_text_input(placeholder):
    input_field = QLineEdit()
    input_field.setFont(BODY_FONT)
    input_field.setPlaceholderText(placeholder)
    input_field.setMinimumWidth(WIDTH//2)
    return input_field

def on_checkbox_state_changed(state, mod_name):
    if state == 2:  # 2 means checked, 0 means unchecked
        if mod_name in change_map["disable"]:
            change_map["disable"].remove(mod_name)
        else:
            change_map["enable"].append(mod_name)
    else:
        if mod_name in change_map["enable"]:
            change_map["enable"].remove(mod_name)
        else:
            change_map["disable"].append(mod_name)


def on_add_all_state_changed(state, checkbox_list: list[QCheckBox]):
    if state == 2:
        for checkbox in checkbox_list:
            checkbox.setChecked(True)
    else:
        for checkbox in checkbox_list:
            checkbox.setChecked(False)


def show_popup():
    # Create a QMessageBox
    popup = QMessageBox()
    popup.setWindowTitle("Confirmation")
    popup.setText("Do you want to delete unwanted mods?")
    popup.setFont(BODY_FONT)

    # Add "Yes" and "No" buttons
    yes_button = popup.addButton("Yes", QMessageBox.ButtonRole.YesRole)
    no_button = popup.addButton("No", QMessageBox.ButtonRole.NoRole)

    # Connect buttons to custom functions
    yes_button.clicked.connect(on_yes_clicked)
    no_button.clicked.connect(on_no_clicked)

    # Show the pop-up
    popup.exec()


def on_confirm_clicked(cancel_button: QPushButton):
    global change_map, delete
    mods_to_be_enabled = change_map["enable"]
    mods_to_be_disabled = change_map["disable"]

    error = False
    for mod in mods_to_be_enabled:
        cancel_button.setDisabled(True)
        try:
            install_mod(mod)
        except Exception as e:
            error = True
            print(f"\033[31m{e}\033[0m")
    if not error and len(mods_to_be_enabled) > 0:
        print(f"\033[32m Mods {mods_to_be_enabled} installed!\033[0m")

    if len(mods_to_be_disabled) > 0:
        show_popup()
    for mod in mods_to_be_disabled:
        cancel_button.setDisabled(True)
        try:
            uninstall_mod(mod, delete)
        except Exception as e:
            error = True
            print(f"\033[31m{e}\033[0m")
    if not error and len(mods_to_be_disabled) > 0:
        print(f"\033[32m Mods {mods_to_be_disabled} uninstalled!\033[0m")
    change_map = reset_map()
    cancel_button.setDisabled(False)


def on_yes_clicked():
    global delete
    delete = True


def on_no_clicked():
    global delete
    delete = False


def on_cancel_clicked():
    sys.exit(0)


def create_button(text):
    button = QPushButton(text)
    button.setFont(BUTTON_FONT)
    button.setFixedWidth(WIDTH//16)
    button.setStyleSheet("""
    QPushButton {
            padding: 10px;
                         margin-top: 10px;
                         margin-bottom:10px;
        }
        """)
    return button


def reset_map():
    return {
        "enable": [],    # Keeps a list of mod_names to be enabled
        "disable": []    # Keeps a list of mod_named to be disabled
    }

def show_settings_popup():
        dialog = SettingsDialog()
        dialog.exec()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")

        # Create layout
        layout = QVBoxLayout()

        # Add text inputs with labels
        MOD_FOLDER, MEDIA_FOLDER, MESH_ZIP, TEXTURE_ZIP = get_paths()
        self.mod_folder_input = create_text_input(MOD_FOLDER)
        self.media_folder_input = create_text_input(MEDIA_FOLDER)
        self.mesh_zip_input = create_text_input(MESH_ZIP)
        self.texture_zip_input = create_text_input(TEXTURE_ZIP)

        mod_hbox = QHBoxLayout()
        mod_hbox.addWidget(create_label("Mod Folder:", BODY_FONT))
        mod_hbox.addStretch()
        mod_hbox.addWidget(self.mod_folder_input)
        layout.addLayout(mod_hbox)
        media_hbox = QHBoxLayout()
        media_hbox.addWidget(create_label("Media Folder:", BODY_FONT))
        media_hbox.addStretch()
        media_hbox.addWidget(self.media_folder_input)
        layout.addLayout(media_hbox)
        mesh_hbox = QHBoxLayout()
        mesh_hbox.addWidget(create_label("Mesh ZIP:", BODY_FONT))
        mesh_hbox.addStretch()
        mesh_hbox.addWidget(self.mesh_zip_input)
        layout.addLayout(mesh_hbox)
        texture_hbox = QHBoxLayout()
        texture_hbox.addWidget(create_label("Texture ZIP:", BODY_FONT))
        texture_hbox.addStretch()
        texture_hbox.addWidget(self.texture_zip_input)
        layout.addLayout(texture_hbox)

        # Add Confirm and Cancel buttons
        hbox = QHBoxLayout()
        confirm_button = create_button("Confirm")
        cancel_button = create_button("Cancel")
        hbox.addWidget(confirm_button)
        hbox.addWidget(cancel_button)
        confirm_button.clicked.connect(self.on_confirm)
        cancel_button.clicked.connect(self.reject)

        layout.addLayout(hbox)

        self.setLayout(layout)

    def on_confirm(self):
        # Get values from text inputs
        mod_folder = self.mod_folder_input.text()
        media_folder = self.media_folder_input.text()
        mesh_zip = self.mesh_zip_input.text()
        texture_zip = self.texture_zip_input.text()

        # Call the update_paths function with the input values
        update_paths(mod_folder, media_folder, mesh_zip, texture_zip)

        # Close the dialog
        self.accept()


class ScrollableWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a scroll area
        scroll_area = QScrollArea(self)
        # Allow the widget to resize with the scroll area
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the content
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                                  background-color: transparent;
            }
            """)
        scroll_area.setWidget(content_widget)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border-radius:10px;
                                  border: 2px solid grey;
                                  background-color: transparent;
            }
            """)

        # Create a layout for the content widget
        content_layout = QVBoxLayout(content_widget)

        df = pd.read_csv(MODS_TABLE)

        for index, row in df.iterrows():
            content = create_list_element(row)
            content_layout.addLayout(content)
            line = create_line()
            content_layout.addWidget(line)

        content_layout.addStretch()

        # Set up the layout for the ScrollableWindow
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Spintires Original Mod Manager")
        self.setGeometry(WIDTH//4, HEIGHT//4, WIDTH//2, round(HEIGHT/1.5))

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a main layout for the central widget
        main_layout = QVBoxLayout(central_widget)

        vbox_list = QVBoxLayout()
        label_list = create_label("Mods List", TITLE_FONT)

        header_hbox = QHBoxLayout()
        header_label = create_label("Mod names", BODY_FONT)
        header_label.setStyleSheet("""
        QLabel {
                            margin-left: 5px;
                            background-color: transparent;
        }
        """)
        header_hbox.addWidget(header_label)
        header_hbox.addStretch()
        add_all = QCheckBox("Add all")
        add_all.setFont(BUTTON_FONT)
        add_all.setStyleSheet("""
        QCheckBox {
                            margin-right: 5px;
                            background-color: transparent;
        }
        """)
        header_hbox.addWidget(add_all)

        scroll_list = ScrollableWindow()
        vbox_list.addWidget(label_list)
        vbox_list.addLayout(header_hbox)
        vbox_list.addWidget(scroll_list)

        # Add the HBoxLayout to the main layout
        main_layout.addLayout(vbox_list)

        add_all.stateChanged.connect(
            lambda state, param="checkbox_list": on_add_all_state_changed(state, checkbox_list))

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        settings_button = create_button("Settings")
        confirm_button = create_button("Confirm")
        cancel_button = create_button("Cancel")
        confirm_button.clicked.connect(
            lambda param="cancel_button": on_confirm_clicked(cancel_button))
        cancel_button.clicked.connect(on_cancel_clicked)
        settings_button.clicked.connect(show_settings_popup)
        button_layout.addWidget(settings_button)
        button_layout.addStretch()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        terminal_textarea = TerminalOutputWidget()
        main_layout.addWidget(terminal_textarea)
        main_layout.addLayout(button_layout)


if __name__ == "__main__":
    global change_map, checkbox_list
    change_map = reset_map()
    checkbox_list = []
    user32 = ctypes.windll.user32
    WIDTH, HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    app = QApplication(sys.argv)
    init_database()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
