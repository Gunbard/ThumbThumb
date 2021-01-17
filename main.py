# ThumbThumb
# External dependencies: ffmpeg, vcsi
# 
import os, sys, subprocess, asyncio, quamash
from mainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets

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
    
    if state == True:
        ui.buttonGenerate.setText("Cancel")
    else:
        ui.buttonGenerate.setText("Generate")

def command_finished(status):
    print("DONE")
    print(status)
    set_processing_mode(False)
    ui.statusBar.showMessage("Contact sheet generation complete!")


async def test_command():    
    proc = await asyncio.create_subprocess_shell(
        "vcsi test.webm -t -w 850 -g 4x4 --background-color 000000 --metadata-font-color ffffff")
    returncode = await proc.wait()
    print(returncode)

def on_button_clicked():
    if ui.progressBar.isVisible() == True:
        ui.progressBar.setVisible(False)
    else:
        set_processing_mode(True)
        ui.statusBar.showMessage("Working...")

        #loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(test_command())
        task.add_done_callback(command_finished)  
        #loop.run_until_complete(task)
        #loop.close()
        
    
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
    
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling);
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
ui.buttonGenerate.clicked.connect(on_button_clicked)
ui.buttonBrowseSource.clicked.connect(on_browse_source)
ui.buttonBrowseOutput.clicked.connect(on_browse_output)

MainWindow.show()
#sys.exit(app.exec_())

with loop:
    loop.run_forever()
    