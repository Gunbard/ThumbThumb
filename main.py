# ThumbThumb
# External dependencies: mtn-win32
# 
import os, sys, subprocess, asyncio, quamash
from mainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets

DEFAULT_EXTS = ["mp4", "mkv", "webm"]

def scan_dir():
    #stub
    return    

def set_processing_mode(state):
    ui.buttonBrowseSource.setEnabled(not state)
    ui.buttonBrowseOutput.setEnabled(not state)
    ui.progressBar.setVisible(state)
    ui.checkboxSubfolders.setEnabled(not state)
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
    progress = ui.progressBar.value()
    ui.progressBar.setValue(progress + 1)
    ui.statusBar.showMessage("Processing {} file(s)...".format(ui.progressBar.maximum() - ui.progressBar.value()))
    if ui.progressBar.value() == ui.progressBar.maximum():
        set_processing_mode(False)
        ui.statusBar.showMessage("Contact sheet generation complete!")

async def process_file(file, input_path, output_path):    
    #command = "vcsi {}\{} -t -w 850 -g 4x4 --background-color 000000 " \
    #    "--metadata-font-color ffffff -o {}\{}.jpg".format(input_path, file, output_path, file)
    command = "mtn.exe -P -r 4 {}\\{} -O {}".format(input_path, file, output_path)
    print(command)
    proc = await asyncio.create_subprocess_shell(command)
    returncode = await proc.wait()
    print(returncode)

def on_generate():
    if ui.progressBar.isVisible() == True:
        ui.progressBar.setVisible(False)
    else:
        filesToProcess = []
        files = os.listdir(ui.fieldSource.text())
        for file in files:
            filename, file_extension = os.path.splitext(file)
            ext = file_extension[1:] # Exclude dot
            ext_filter_text = ui.fieldExtensionFilter.text()
            if len(ext_filter_text) > 0:
                extensions = map(str.strip, ext_filter_text.split(",")) # Remove whitespace
                if ext in extensions:
                    filesToProcess.append(file)
            else:
                if ext in DEFAULT_EXTS:
                    filesToProcess.append(file)
        print(filesToProcess)

        set_processing_mode(True)
        ui.progressBar.setValue(0)
        ui.progressBar.setRange(0, len(filesToProcess))
        ui.statusBar.showMessage("Starting processing of {} file(s)...".format(len(filesToProcess)))
        for file in filesToProcess:
            task = asyncio.ensure_future(process_file(file, ui.fieldSource.text(), ui.fieldOutput.text()))
            task.add_done_callback(command_finished)
    
def on_browse_source():
    path = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Source Directory"))
    if path == "":
        path = os.getcwd()
    ui.fieldSource.setText(os.path.normpath(path))
    ui.buttonGenerate.setEnabled(True)
    
def on_browse_output():
    path = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Output Directory"))
    if path == "":
        path = os.getcwd()
    ui.fieldOutput.setText(os.path.normpath(path))
    
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QtWidgets.QApplication(sys.argv)
loop = quamash.QEventLoop(app)
asyncio.set_event_loop(loop)

MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
ui.progressBar.setVisible(False)
ui.fieldOutput.setText(os.getcwd())
ui.buttonGenerate.setEnabled(False)

# BUTTON EVENTS
ui.buttonGenerate.clicked.connect(on_generate)
ui.buttonBrowseSource.clicked.connect(on_browse_source)
ui.buttonBrowseOutput.clicked.connect(on_browse_output)

MainWindow.show()

with loop:
    loop.run_forever()
    