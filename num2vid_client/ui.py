"""PySide2 UI for Num2Vid Client for sending integers to Num2Vid Server and downlloading result.

Requires the num2vid module to be available in PYTHONPATH. It is reccomended to start using
launcher.py. For help using this tool, navigate a terminal to the repo root and type:
    `<python3 executable> launcher.py --help`
"""
import random
import sys
from os import path as osp
from os import environ

from PySide2 import QtCore, QtWidgets

from num2vid import Num2VidClient


class Num2VidClientUI(QtWidgets.QWidget):
    """Num2Vid UI.

    :param _core: Num2VidClient isntance.
    :param _label_instructions: User instructions textblock.
    :param _vid_save_path: Selected vid save path from file save dialog.
    :param btn_submit: Submit button to send math expression string to server.
    :param spinbox_num: Specific widget for entering digits with keyboard & mouse functionality
    """
    def __init__(self, config_path: str):
        """Initialize with default widget values, then set up UI."""
        super().__init__()
        self._core = Num2VidClient(config_path)  # core client api
        self._label_instructions = QtWidgets.QLabel(self._core.config.get("label_instructions"))
        self._vid_save_path = None
        self.btn_submit = QtWidgets.QPushButton("Submit Num to Server.")
        self.spinbox_num = QtWidgets.QSpinBox()
        self.__setup_ui()

    def __setup_ui(self):
        """Set up UI."""
        # since we won't be manipulating our layout don't we don't need to assign it to instance.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label_instructions)
        layout.addWidget(self.spinbox_num)
        layout.addWidget(self.btn_submit)
        self.setLayout(layout)

        # set default settings
        num_min = self._core.config.get("num_min")
        num_max = self._core.config.get("num_max")
        self.spinbox_num.setMinimum(num_min)
        self.spinbox_num.setMaximum(num_max)
        self.spinbox_num.setValue(random.choice(range(num_min, num_max)))  # set random default num
        self._label_instructions.setAlignment(QtCore.Qt.AlignCenter)
        self.btn_submit.clicked.connect(self.submit_num)

    def apply_config(self):
        """Save the current config settings to disk."""
        self._core.config.save(self._config)

    def get_vid_save_location(self, num: int) -> str:
        """Open OS-native file save dialog and return filepath.

        :param num: entered int from spinbox.
        """
        return QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save vid...",  # window title
            osp.join(osp.expanduser("~"), "{num}.{ext}".format(
                num=num,
                ext=self._core.config.get("vid_format"))),  # default directory
            "Video Files (*.mp4)")[0]  # filetype filter

    def submit_num(self) -> str:
        """Submit num to Num2Vid server via http GET request for resulting vid."""
        num = self.spinbox_num.value()
        # call model
        res = self._core.submit_num(num)
        # prompt user for file save location
        self._vid_save_path = self.get_vid_save_location(num)
        with open(self._vid_save_path, "wb") as yay:
            yay.write(res.content)  # write contents from server directly to file

        return self._vid_save_path


if __name__ == "__main__":
    APP = QtWidgets.QApplication([])
    WIDGET = Num2VidClientUI(environ["NUM2VID_CONFIG"])
    WIDGET.resize(400, 100)
    WIDGET.show()

    sys.exit(APP.exec_())
