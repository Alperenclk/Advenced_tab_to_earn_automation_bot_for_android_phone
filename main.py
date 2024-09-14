import sys
import os
import json
import pyautogui
import time
import cv2
import numpy as np
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

scrcpy_exe_path = os.path.abspath("scrcpy-win64-v2.4\\scrcpy.exe")


class Operation:
    def __init__(self, op_type, name, **kwargs):
        self.type = op_type
        self.name = name
        self.params = kwargs


class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.operations = []
        self.selected_operations = []
        self.stop_flag = False
        self.init_ui()
        self.scrcpy_process = None
        self.start_scrcpy()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        upper_layout = QtWidgets.QVBoxLayout()
        op_buttons_layout = QtWidgets.QGridLayout()

        btn_add_click = QtWidgets.QPushButton("Add Click")
        btn_add_click.clicked.connect(self.add_click)

        btn_add_text = QtWidgets.QPushButton("Write Text")
        btn_add_text.clicked.connect(self.add_text)

        btn_add_wait = QtWidgets.QPushButton("Add Wait")
        btn_add_wait.clicked.connect(self.add_wait)

        btn_add_find = QtWidgets.QPushButton("Add Find")
        btn_add_find.clicked.connect(self.add_find)

        btn_add_if = QtWidgets.QPushButton("Add If")
        btn_add_if.clicked.connect(self.add_if)

        btn_add_else = QtWidgets.QPushButton("Add Else")
        btn_add_else.clicked.connect(self.add_else)

        btn_add_endif = QtWidgets.QPushButton("Add End If")
        btn_add_endif.clicked.connect(self.add_endif)

        btn_add_while = QtWidgets.QPushButton("Add While")
        btn_add_while.clicked.connect(self.add_while)

        btn_add_endwhile = QtWidgets.QPushButton("Add End While")
        btn_add_endwhile.clicked.connect(self.add_endwhile)

        btn_add_for = QtWidgets.QPushButton("Add For")
        btn_add_for.clicked.connect(self.add_for)

        btn_add_endfor = QtWidgets.QPushButton("Add End For")
        btn_add_endfor.clicked.connect(self.add_endfor)

        btn_save = QtWidgets.QPushButton("Save Automation")
        btn_save.clicked.connect(self.save_automation)

        btn_load = QtWidgets.QPushButton("Load Automation")
        btn_load.clicked.connect(self.load_automation)

        buttons = [
            btn_add_click,
            btn_add_text,
            btn_add_wait,
            btn_add_find,
            btn_add_if,
            btn_add_else,
            btn_add_endif,
            btn_add_while,
            btn_add_endwhile,
            btn_add_for,
            btn_add_endfor,
            btn_save,
            btn_load,
        ]

        for idx, button in enumerate(buttons):
            row = idx // 4
            col = idx % 4
            op_buttons_layout.addWidget(button, row, col)

        upper_layout.addLayout(op_buttons_layout)

        self.op_list_widget = QtWidgets.QListWidget()
        upper_layout.addWidget(self.op_list_widget)

        lower_layout = QtWidgets.QVBoxLayout()
        lbl = QtWidgets.QLabel("Arrange Operations:")
        lower_layout.addWidget(lbl)
        self.selected_op_list_widget = QtWidgets.QListWidget()
        lower_layout.addWidget(self.selected_op_list_widget)
        arrange_buttons_layout = QtWidgets.QHBoxLayout()
        btn_add_to_sequence = QtWidgets.QPushButton("Add to Sequence")
        btn_add_to_sequence.clicked.connect(self.add_to_sequence)
        btn_remove_from_sequence = QtWidgets.QPushButton("Remove from Sequence")
        btn_remove_from_sequence.clicked.connect(self.remove_from_sequence)
        btn_run = QtWidgets.QPushButton("Run Automation")
        btn_run.clicked.connect(self.run_automation)
        arrange_buttons_layout.addWidget(btn_add_to_sequence)
        arrange_buttons_layout.addWidget(btn_remove_from_sequence)
        arrange_buttons_layout.addWidget(btn_run)
        lower_layout.addLayout(arrange_buttons_layout)

        main_layout.addLayout(upper_layout)
        main_layout.addLayout(lower_layout)

        self.resize(800, 600)
        self.show()

    def start_scrcpy(self):
        self.scrcpy_process = QtCore.QProcess(self)
        scrcpy_command = [
            scrcpy_exe_path,
            "--prefer-text",
            "--window-title=scrcpy",
            # "--always-on-top",
        ]
        self.scrcpy_process.start(scrcpy_command[0], scrcpy_command[1:])
        self.scrcpy_process.started.connect(self.position_windows)
        self.scrcpy_process.errorOccurred.connect(self.handle_scrcpy_error)

    def position_windows(self):
        try:
            import pygetwindow as gw

            time.sleep(1)
            scrcpy_windows = gw.getWindowsWithTitle("scrcpy")
            if not scrcpy_windows:
                raise Exception("Scrcpy window not found")
            scrcpy_window = scrcpy_windows[0]
            screen = QtWidgets.QApplication.desktop().screenGeometry()
            scrcpy_width = 400
            scrcpy_height = 800
            total_width = scrcpy_width + self.width() + 20
            scrcpy_x = (screen.width() - total_width) // 2
            scrcpy_y = (screen.height() - scrcpy_height) // 2
            scrcpy_window.resizeTo(scrcpy_width, scrcpy_height)
            scrcpy_window.moveTo(scrcpy_x, scrcpy_y)
            app_x = scrcpy_x + scrcpy_width + 20
            app_y = scrcpy_y
            self.move(app_x, app_y)
        except Exception as e:
            print(f"Failed to position windows: {e}")

    def handle_scrcpy_error(self, error):
        QtWidgets.QMessageBox.critical(
            self, "Error", f"Failed to start scrcpy: {error}"
        )

    def add_click(self):
        try:
            import pygetwindow as gw

            scrcpy_windows = gw.getWindowsWithTitle("scrcpy")
            if not scrcpy_windows:
                raise Exception("Scrcpy window not found")
            scrcpy_window = scrcpy_windows[0]
            scrcpy_x = scrcpy_window.left
            scrcpy_y = scrcpy_window.top
            scrcpy_width = scrcpy_window.width
            scrcpy_height = scrcpy_window.height
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Scrcpy window not found: {e}"
            )
            return

        self.overlay = OverlayWidget(scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height)
        self.overlay.clicked.connect(self.on_click_position)
        self.overlay.show()

    def on_click_position(self, x, y):
        self.overlay.close()
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Click Details")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        name_edit = QtWidgets.QLineEdit()
        click_option_group = QtWidgets.QButtonGroup(dialog)
        clicks_radio = QtWidgets.QRadioButton("Number of clicks")
        duration_radio = QtWidgets.QRadioButton("Duration (seconds)")
        clicks_radio.setChecked(True)
        click_option_group.addButton(clicks_radio)
        click_option_group.addButton(duration_radio)
        clicks_edit = QtWidgets.QLineEdit("1")
        duration_edit = QtWidgets.QLineEdit("0")
        interval_edit = QtWidgets.QLineEdit("100")
        layout.addRow("Name:", name_edit)
        layout.addRow(clicks_radio, clicks_edit)
        layout.addRow(duration_radio, duration_edit)
        layout.addRow("Interval between clicks (ms):", interval_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_edit.text()
            if not name:
                QtWidgets.QMessageBox.critical(dialog, "Error", "Name cannot be empty.")
                return
            interval = int(interval_edit.text())
            if clicks_radio.isChecked():
                try:
                    clicks = int(clicks_edit.text())
                    if clicks < 1:
                        raise ValueError
                    op = Operation(
                        "click", name, x=x, y=y, clicks=clicks, interval=interval
                    )
                except ValueError:
                    QtWidgets.QMessageBox.critical(
                        dialog, "Error", "Invalid number of clicks."
                    )
                    return
            elif duration_radio.isChecked():
                try:
                    duration = float(duration_edit.text())
                    if duration <= 0:
                        raise ValueError
                    op = Operation(
                        "click", name, x=x, y=y, duration=duration, interval=interval
                    )
                except ValueError:
                    QtWidgets.QMessageBox.critical(dialog, "Error", "Invalid duration.")
                    return
            else:
                QtWidgets.QMessageBox.critical(
                    dialog, "Error", "Please select an option."
                )
                return
            self.operations.append(op)
            self.op_list_widget.addItem(f"Click: {name} at ({x}, {y})")
        else:
            return

    def add_text(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Write Text")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        title_edit = QtWidgets.QLineEdit()
        text_edit = QtWidgets.QLineEdit()
        layout.addRow("Title:", title_edit)
        layout.addRow("Text:", text_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            title = title_edit.text()
            text = text_edit.text()
            if not title or not text:
                QtWidgets.QMessageBox.critical(
                    dialog, "Error", "Title and Text cannot be empty."
                )
                return
            op = Operation("write", title, text=text)
            self.operations.append(op)
            self.op_list_widget.addItem(f"Write Text: {title} - {text}")
        else:
            return

    def add_wait(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Wait")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        name_edit = QtWidgets.QLineEdit()
        duration_edit = QtWidgets.QLineEdit()
        layout.addRow("Name:", name_edit)
        layout.addRow("Duration (seconds):", duration_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_edit.text()
            if not name:
                QtWidgets.QMessageBox.critical(dialog, "Error", "Name cannot be empty.")
                return
            try:
                duration = float(duration_edit.text())
                if duration < 0:
                    raise ValueError
            except ValueError:
                QtWidgets.QMessageBox.critical(dialog, "Error", "Invalid duration.")
                return
            op = Operation("wait", name, duration=duration)
            self.operations.append(op)
            self.op_list_widget.addItem(f"Wait: {name}, Duration: {duration}s")
        else:
            return

    def add_find(self):
        try:
            import pygetwindow as gw

            scrcpy_windows = gw.getWindowsWithTitle("scrcpy")
            if not scrcpy_windows:
                raise Exception("Scrcpy window not found")
            scrcpy_window = scrcpy_windows[0]
            scrcpy_x = scrcpy_window.left
            scrcpy_y = scrcpy_window.top
            scrcpy_width = scrcpy_window.width
            scrcpy_height = scrcpy_window.height
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Scrcpy window not found: {e}"
            )
            return

        self.overlay = SelectionOverlay(scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height)
        self.overlay.selection_made.connect(self.on_selection_made)
        self.overlay.show()

    def on_selection_made(self, x, y, w, h, screenshot):
        self.overlay.close()
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Find Details")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        name_edit = QtWidgets.QLineEdit()
        layout.addRow("Name:", name_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_edit.text()
            if not name:
                QtWidgets.QMessageBox.critical(dialog, "Error", "Name cannot be empty.")
                return
            template_path = f"templates/{name}.png"
            if not os.path.exists("templates"):
                os.makedirs("templates")
            cv2.imwrite(template_path, screenshot)
            op = Operation("find", name, template=template_path)
            self.operations.append(op)
            self.op_list_widget.addItem(f"Find: {name}")
        else:
            return

    def add_if(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("If Condition")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        condition_edit = QtWidgets.QComboBox()
        find_operations = [op.name for op in self.operations if op.type == "find"]
        if not find_operations:
            QtWidgets.QMessageBox.critical(
                dialog, "Error", "No 'Find' operations available."
            )
            return
        condition_edit.addItems(find_operations)
        layout.addRow("Select Find Operation:", condition_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_find = condition_edit.currentText()
            op = Operation("if", f"If {selected_find}", condition=selected_find)
            self.selected_operations.append(op)
            self.selected_op_list_widget.addItem(f"If {selected_find}")
        else:
            return

    def add_else(self):
        op = Operation("else", "Else")
        self.selected_operations.append(op)
        self.selected_op_list_widget.addItem("Else")

    def add_endif(self):
        op = Operation("endif", "End If")
        self.selected_operations.append(op)
        self.selected_op_list_widget.addItem("End If")

    def add_while(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("While Loop")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        condition_edit = QtWidgets.QComboBox()
        find_operations = [op.name for op in self.operations if op.type == "find"]
        if not find_operations:
            QtWidgets.QMessageBox.critical(
                dialog, "Error", "No 'Find' operations available."
            )
            return
        condition_edit.addItems(find_operations)
        layout.addRow("Select Find Operation:", condition_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_find = condition_edit.currentText()
            op = Operation("while", f"While {selected_find}", condition=selected_find)
            self.selected_operations.append(op)
            self.selected_op_list_widget.addItem(f"While {selected_find}")
        else:
            return

    def add_endwhile(self):
        op = Operation("endwhile", "End While")
        self.selected_operations.append(op)
        self.selected_op_list_widget.addItem("End While")

    def add_for(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("For Loop")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        layout = QtWidgets.QFormLayout(dialog)
        iterations_edit = QtWidgets.QLineEdit("1")
        layout.addRow("Number of iterations:", iterations_edit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            dialog,
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog.move(self.x() + 50, self.y() + 50)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            try:
                iterations = int(iterations_edit.text())
                if iterations < 1:
                    raise ValueError
                op = Operation("for", f"For {iterations}", iterations=iterations)
                self.selected_operations.append(op)
                self.selected_op_list_widget.addItem(f"For {iterations}")
            except ValueError:
                QtWidgets.QMessageBox.critical(
                    dialog, "Error", "Invalid number of iterations."
                )
        else:
            return

    def add_endfor(self):
        op = Operation("endfor", "End For")
        self.selected_operations.append(op)
        self.selected_op_list_widget.addItem("End For")

    def add_to_sequence(self):
        selected_items = self.op_list_widget.selectedItems()
        for item in selected_items:
            index = self.op_list_widget.row(item)
            op = self.operations[index]
            self.selected_operations.append(op)
            self.selected_op_list_widget.addItem(item.text())

    def remove_from_sequence(self):
        selected_items = self.selected_op_list_widget.selectedItems()
        for item in selected_items:
            index = self.selected_op_list_widget.row(item)
            self.selected_operations.pop(index)
            self.selected_op_list_widget.takeItem(index)

    def run_automation(self):
        self.stop_flag = False

        def automation():
            try:
                import pygetwindow as gw

                scrcpy_windows = gw.getWindowsWithTitle("scrcpy")
                if not scrcpy_windows:
                    raise Exception("Scrcpy window not found")
                scrcpy_window = scrcpy_windows[0]
                scrcpy_x = scrcpy_window.left
                scrcpy_y = scrcpy_window.top
                scrcpy_width = scrcpy_window.width
                scrcpy_height = scrcpy_window.height
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Scrcpy window not found: {e}"
                )
                return

            skip_stack = []
            loop_stack = []
            i = 0
            while i < len(self.selected_operations):
                if self.stop_flag or keyboard.is_pressed("esc"):
                    self.stop_flag = True
                    break
                op = self.selected_operations[i]
                if op.type == "if":
                    condition_result = None
                    find_op_name = op.params.get("condition", "")
                    find_op = next(
                        (
                            o
                            for o in self.operations
                            if o.name == find_op_name and o.type == "find"
                        ),
                        None,
                    )
                    if find_op:
                        condition_result = self.perform_find(
                            find_op, scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height
                        )
                    else:
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Error",
                            f"'Find' operation '{find_op_name}' not found.",
                        )
                        return
                    if not condition_result:
                        skip_stack.append("if")
                    i += 1
                    continue
                elif op.type == "else":
                    if skip_stack and skip_stack[-1] == "if":
                        skip_stack.pop()
                        skip_stack.append("else")
                    elif skip_stack and skip_stack[-1] == "else":
                        skip_stack.pop()
                    i += 1
                    continue
                elif op.type == "endif":
                    if skip_stack and (
                        skip_stack[-1] == "if" or skip_stack[-1] == "else"
                    ):
                        skip_stack.pop()
                    i += 1
                    continue
                elif op.type == "while":
                    loop_stack.append(
                        {
                            "type": "while",
                            "start_index": i,
                            "condition": op.params.get("condition", ""),
                        }
                    )
                    i += 1
                    continue
                elif op.type == "endwhile":
                    if loop_stack and loop_stack[-1]["type"] == "while":
                        find_op_name = loop_stack[-1]["condition"]
                        find_op = next(
                            (
                                o
                                for o in self.operations
                                if o.name == find_op_name and o.type == "find"
                            ),
                            None,
                        )
                        if find_op:
                            condition_result = self.perform_find(
                                find_op, scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height
                            )
                        else:
                            QtWidgets.QMessageBox.critical(
                                self,
                                "Error",
                                f"'Find' operation '{find_op_name}' not found.",
                            )
                            return
                        if condition_result:
                            i = loop_stack[-1]["start_index"] + 1
                        else:
                            loop_stack.pop()
                            i += 1
                    else:
                        QtWidgets.QMessageBox.critical(
                            self, "Error", "'End While' without matching 'While'."
                        )
                        return
                    continue
                elif op.type == "for":
                    iterations = op.params.get("iterations", 1)
                    loop_stack.append(
                        {
                            "type": "for",
                            "start_index": i,
                            "iterations": iterations,
                            "counter": 0,
                        }
                    )
                    i += 1
                    continue
                elif op.type == "endfor":
                    if loop_stack and loop_stack[-1]["type"] == "for":
                        loop_info = loop_stack[-1]
                        loop_info["counter"] += 1
                        if loop_info["counter"] < loop_info["iterations"]:
                            i = loop_info["start_index"] + 1
                        else:
                            loop_stack.pop()
                            i += 1
                    else:
                        QtWidgets.QMessageBox.critical(
                            self, "Error", "'End For' without matching 'For'."
                        )
                        return
                    continue

                if skip_stack:
                    i += 1
                    continue

                if op.type == "click":
                    x, y = op.params["x"], op.params["y"]
                    interval = op.params.get("interval", 100) / 1000.0
                    if "clicks" in op.params:
                        clicks = op.params["clicks"]
                        for _ in range(clicks):
                            if self.stop_flag or keyboard.is_pressed("esc"):
                                self.stop_flag = True
                                break
                            pyautogui.click(x=scrcpy_x + x, y=scrcpy_y + y)
                            time.sleep(interval)
                    elif "duration" in op.params:
                        end_time = time.time() + op.params["duration"]
                        while time.time() < end_time:
                            if self.stop_flag or keyboard.is_pressed("esc"):
                                self.stop_flag = True
                                break
                            pyautogui.click(x=scrcpy_x + x, y=scrcpy_y + y)
                            time.sleep(interval)
                    time.sleep(0.5)
                elif op.type == "write":
                    text = op.params["text"]
                    scrcpy_window.activate()
                    time.sleep(0.1)
                    pyautogui.click(scrcpy_x + 10, scrcpy_y + 10)
                    time.sleep(0.1)
                    pyautogui.typewrite(text, interval=0.1)
                    time.sleep(0.5)
                elif op.type == "wait":
                    duration = op.params["duration"]
                    time.sleep(duration)
                elif op.type == "find":
                    pass  # 'Find' operations are handled in 'if' and 'while' conditions
                i += 1

        self.automation_thread = QtCore.QThread()
        self.worker = Worker(automation)
        self.worker.moveToThread(self.automation_thread)
        self.automation_thread.started.connect(self.worker.run)
        self.automation_thread.start()

    def perform_find(self, op, scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height):
        template_path = op.params["template"]
        if not os.path.exists(template_path):
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Template image not found: {template_path}"
            )
            return False
        screenshot = pyautogui.screenshot(
            region=(scrcpy_x, scrcpy_y, scrcpy_width, scrcpy_height)
        )
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if len(loc[0]) > 0:
            op.params["found"] = True
            return True
        else:
            op.params["found"] = False
            return False

    def save_automation(self):
        title, ok = QtWidgets.QInputDialog.getText(self, "Save Automation", "Title:")
        if ok and title:
            options = QtWidgets.QFileDialog.Options()
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Automation",
                title + ".json",
                "JSON Files (*.json)",
                options=options,
            )
            if filename:
                data = [op.__dict__ for op in self.selected_operations]
                with open(filename, "w") as f:
                    json.dump(data, f)
                QtWidgets.QMessageBox.information(
                    self, "Success", "Automation saved successfully."
                )

    def load_automation(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Automation", "", "JSON Files (*.json)", options=options
        )
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
            self.operations = []
            self.op_list_widget.clear()
            self.selected_operations = []
            self.selected_op_list_widget.clear()
            for op_data in data:
                op = Operation(op_data["type"], op_data["name"], **op_data["params"])
                self.operations.append(op)
                self.selected_operations.append(op)
                if op.type == "click":
                    self.op_list_widget.addItem(f"Click: {op.name}")
                elif op.type == "write":
                    self.op_list_widget.addItem(f"Write Text: {op.name}")
                elif op.type == "wait":
                    self.op_list_widget.addItem(f"Wait: {op.name}")
                elif op.type == "find":
                    self.op_list_widget.addItem(f"Find: {op.name}")
                elif op.type == "if":
                    self.op_list_widget.addItem(f"If {op.params.get('condition', '')}")
                elif op.type == "else":
                    self.op_list_widget.addItem("Else")
                elif op.type == "endif":
                    self.op_list_widget.addItem("End If")
                elif op.type == "while":
                    self.op_list_widget.addItem(
                        f"While {op.params.get('condition', '')}"
                    )
                elif op.type == "endwhile":
                    self.op_list_widget.addItem("End While")
                elif op.type == "for":
                    iterations = op.params.get("iterations", 1)
                    self.op_list_widget.addItem(f"For {iterations}")
                elif op.type == "endfor":
                    self.op_list_widget.addItem("End For")
                self.selected_op_list_widget.addItem(
                    self.op_list_widget.item(self.op_list_widget.count() - 1).text()
                )

    def closeEvent(self, event):
        self.stop_flag = True
        if self.scrcpy_process:
            self.scrcpy_process.kill()
            self.scrcpy_process.waitForFinished()
        event.accept()


class Worker(QtCore.QObject):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()


class OverlayWidget(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(int, int)

    def __init__(self, x, y, width, height):
        super().__init__(None)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.setWindowOpacity(0.3)
        self.setGeometry(x, y, width, height)
        self.setCursor(QtCore.Qt.BlankCursor)
        self.crosshair_size = 20
        self.crosshair_color = QtGui.QColor("red")
        self.setMouseTracking(True)
        self.cursor_pos = QtCore.QPoint(self.width() // 2, self.height() // 2)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(self.crosshair_color, 2))
        x = self.cursor_pos.x()
        y = self.cursor_pos.y()
        painter.drawLine(x - self.crosshair_size, y, x + self.crosshair_size, y)
        painter.drawLine(x, y - self.crosshair_size, x, y + self.crosshair_size)

    def mouseMoveEvent(self, event):
        self.cursor_pos = event.pos()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(event.x(), event.y())


class SelectionOverlay(QtWidgets.QWidget):
    selection_made = QtCore.pyqtSignal(int, int, int, int, np.ndarray)

    def __init__(self, x, y, width, height):
        super().__init__(None)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.setWindowOpacity(0.3)
        self.setGeometry(x, y, width, height)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.start_pos = None
        self.end_pos = None
        self.rect = None

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.rect = QtCore.QRect()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()
        self.rect = QtCore.QRect(self.start_pos, self.end_pos)
        self.update()

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.rect = QtCore.QRect(self.start_pos, self.end_pos)
        x = self.rect.left()
        y = self.rect.top()
        w = self.rect.width()
        h = self.rect.height()
        if w > 0 and h > 0:
            screenshot = pyautogui.screenshot(region=(self.x() + x, self.y() + y, w, h))
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.selection_made.emit(x, y, w, h, screenshot)
        self.close()

    def paintEvent(self, event):
        if self.rect:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QColor("red"), 2))
            painter.drawRect(self.rect.normalized())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
