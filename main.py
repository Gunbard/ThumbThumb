# ThumbThumb
# 
import os, sys, subprocess, asyncio, quamash
from mainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets

MAX_BATCH_SIZE = 3
MAX_WALK_DEPTH = 10
DEFAULT_EXTS = ["mp4", "mkv", "webm", "avi", "mov"]

def set_processing_mode(state):
    ui.buttonBrowseSource.setEnabled(not state)
    ui.buttonBrowseOutput.setEnabled(not state)
    ui.progressBar.setVisible(state)
    ui.checkboxSubfolders.setEnabled(not state)
    ui.checkboxKeepStructure.setEnabled(ui.checkboxSubfolders.isEnabled() and ui.checkboxSubfolders.isChecked())
    ui.checkboxPrefixFilename.setEnabled(ui.checkboxSubfolders.isEnabled() and ui.checkboxSubfolders.isChecked())
    ui.fieldOutput.setEnabled(not state)
    ui.fieldSource.setEnabled(not state)
    ui.fieldExtensionFilter.setEnabled(not state)
    
    if state == True:
        ui.buttonGenerate.setText("Cancel")
    else:
        ui.buttonGenerate.setText("Generate")

def command_finished(status):
    print("DONE")
    print(status)
    
    if ui.progressBar.isVisible():
        progress = ui.progressBar.value()
        ui.progressBar.setValue(progress + 1)
        filesLeft = ui.progressBar.maximum() - ui.progressBar.value()
        ui.statusBar.showMessage("Processing {} file(s)...".format(filesLeft))
        MainWindow.setWindowTitle("{} file(s) left ({})".format(filesLeft, ui.progressBar.text()))
        if ui.progressBar.value() == ui.progressBar.maximum():
            set_processing_mode(False)
            ui.buttonGenerate.setEnabled(True)
            ui.statusBar.showMessage("Generation complete! {} file(s) failed to generate.".format(len(failedFiles)))
            MainWindow.setWindowTitle(app.applicationName())
            if (len(failedFiles) > 0):
                message = ""
                for file in failedFiles:
                    message += file + os.linesep
                dialog = QtWidgets.QMessageBox()
                dialog.setIcon(QtWidgets.QMessageBox.Critical)
                dialog.setWindowTitle("Failed Files")
                dialog.setText(message)
                dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
                dialog.exec()

async def process_file(full_file_path, input_path, output_path, keep_structure, prefix_dirname, semaphore):
    async with semaphore:   
        root, file = os.path.split(full_file_path)
        output_file = os.path.relpath(full_file_path, input_path) if keep_structure else file
        new_dir = os.path.join(output_path, os.path.dirname(output_file))

        # Create subfolders in output folder if needed
        if keep_structure:
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)

        if prefix_dirname:
            # Prefix the output filename with the name of the folder it's in
            subdir = os.path.dirname(os.path.relpath(full_file_path, input_path))
            if len(subdir) > 0:
                output_file = "{}-{}".format(os.path.relpath(subdir, os.path.dirname(subdir)), os.path.basename(output_file))
                if keep_structure:
                    output_file = os.path.join(subdir, output_file)

        command = "vcsi \"{}\" -t -w 850 -g 4x4 --no-overwrite --background-color 000000 " \
            "--metadata-font-color ffffff -o \"{}\\{}.jpg\"".format(full_file_path, output_path, output_file)
        proc = await asyncio.create_subprocess_shell(command)
        returncode = await proc.wait()
        if returncode > 0:
            failedFiles.append(full_file_path) 

def valid_folders():
    if len(ui.fieldSource.text()) == 0 or len(ui.fieldOutput.text()) == 0:
        ui.statusBar.showMessage("Source and Output folders must be set!")
        return False
    else:
        ui.statusBar.clearMessage()
        return True

def validate_files(path, files):
    valid_files = []
    for file in files:
        filename, file_extension = os.path.splitext(file)
        ext = file_extension[1:] # Exclude dot
        ext_filter_text = ui.fieldExtensionFilter.text()
        if len(ext_filter_text) > 0:
            extensions = map(str.strip, ext_filter_text.split(",")) # Remove whitespace
            if ext in extensions:
                valid_files.append(os.path.join(path, file))
        else:
            if ext in DEFAULT_EXTS:
                valid_files.append(os.path.join(path, file))
    return valid_files

def on_generate():
    if ui.progressBar.isVisible() == True:
        pending_tasks = asyncio.all_tasks(loop)
        for task in pending_tasks:
            task.cancel()
        ui.statusBar.showMessage("Contact sheet generation cancelled.")
        MainWindow.setWindowTitle(app.applicationName())
        set_processing_mode(False)
    else:
        failedFiles.clear()
        filesToProcess = []
        if ui.checkboxSubfolders.isChecked() == True:
            source = ui.fieldSource.text()
            for root, dirs, files in os.walk(source):
                if root[len(source):].count(os.sep) < MAX_WALK_DEPTH:
                    path = root.split(os.sep)
                    print((len(path) - 1) * '---', os.path.basename(root))
                    filesToProcess.extend(validate_files(root, files))
        else:
            filesToProcess = validate_files(ui.fieldSource.text(), os.listdir(ui.fieldSource.text()))
        print(filesToProcess)

        if len(filesToProcess) == 0:
            ui.statusBar.showMessage("No valid files found in source folder!")
            return

        set_processing_mode(True)
        ui.progressBar.setValue(0)
        ui.progressBar.setRange(0, len(filesToProcess))
        ui.statusBar.showMessage("Starting processing {} file(s)...".format(len(filesToProcess)))
        for file in filesToProcess:
            task = asyncio.ensure_future(process_file(file, ui.fieldSource.text(), ui.fieldOutput.text(), ui.checkboxKeepStructure.isChecked(), ui.checkboxPrefixFilename.isChecked(), asyncio_semaphore))
            task.add_done_callback(command_finished)
            #asyncio.run(process_file(file, ui.fieldSource.text(), ui.fieldOutput.text()))
    
def on_browse_source():
    path = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Source Directory"))
    if path == "":
        path = os.getcwd()
    ui.fieldSource.setText(os.path.normpath(path))
    
def on_browse_output():
    path = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Output Directory"))
    if path == "":
        path = os.getcwd()
    ui.fieldOutput.setText(os.path.normpath(path))

def on_checkboxSubfolders_changed():
    checked = ui.checkboxSubfolders.isChecked()
    ui.checkboxKeepStructure.setEnabled(checked)
    ui.checkboxPrefixFilename.setEnabled(checked)

    if not checked:
        ui.checkboxKeepStructure.setChecked(False)
        ui.checkboxPrefixFilename.setChecked(False)

def on_field_changed(newText):
    ui.buttonGenerate.setEnabled(valid_folders())

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication(sys.argv)
loop = quamash.QEventLoop(app)
asyncio.set_event_loop(loop)
asyncio_semaphore = asyncio.Semaphore(MAX_BATCH_SIZE)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
ui.progressBar.setVisible(False)
ui.fieldOutput.setText(os.getcwd())
ui.buttonGenerate.setEnabled(False)

# EVENTS
ui.buttonGenerate.clicked.connect(on_generate)
ui.buttonBrowseSource.clicked.connect(on_browse_source)
ui.buttonBrowseOutput.clicked.connect(on_browse_output)
ui.checkboxSubfolders.stateChanged.connect(on_checkboxSubfolders_changed)
ui.fieldSource.textChanged.connect(on_field_changed)
ui.fieldOutput.textChanged.connect(on_field_changed)

# Globals
failedFiles = []

MainWindow.show()

with loop:
    loop.run_forever()
    