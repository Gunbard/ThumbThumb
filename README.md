# ThumbThumb
### Generate video contact sheets for entire folders
##### ThumbThumb digs through a folder of video files and generates a sheet of thumbnails for each one making it easy to preview a huge set of videos at a glance!
![alt text](https://raw.github.com/Gunbard/ThumbThumb/master/readme-img/screencap-0.1.0.png "Windows 10 screenshot")
##### Tested with Python 3.8.6/venv on Windows 10
See the vcsi project in GitHub for sample output files: https://github.com/amietn/vcsi

### Features
- Generate contact sheets/thumbnail sheets for a folder full of video clips, movies, dirty stuff, etc.
- Search through subdirectories (currently limited to 10 to prevent issues with heavily nested subfolders)
- Prefix the folder name to the output image (useful for similarly named files like Ep 1.mkv, Ep 2.mkv, etc.)
- Keep the folder structure of the source content in the output folder

### Dependencies
```sh
pip3 install -r requirements.txt
```
### External Dependencies
These should be somewhere in your system PATH
- vcsi (https://github.com/amietn/vcsi)
- ffmpeg and ffprobe (https://ffmpeg.org/)

### Running
```sh
python3 main.py
```

### Building with PyInstaller
```sh
pip3 install pyinstaller
```

##### Precompile vcsi
```sh
git clone https://github.com/amietn/vcsi.git
pyinstaller --onefile vcsi/vcsi.py
```
Look in the "dist" folder for vcsi.exe

#### Build
Place vcsi.exe, the [VERSION](https://github.com/amietn/vcsi/blob/master/vcsi/VERSION) file from the vcsi project, ffmpeg.exe, and ffprobe.exe in project root

##### Single executable
```sh
pyinstaller --add-binary "vcsi.exe;." --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --onefile main.py
```
The VERSION file must be in the same directory as the output main.exe.

##### Packaged folder
```sh
pyinstaller --add-binary "vcsi.exe;." --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --add-data "VERSION;." --onedir main.py
```

Your distributable executable or folder should be in the "dist" directory. Don't forget to include the VERSION file if distributing the single exe.

Rebuild after making any changes with:
```sh
pyinstaller main.spec
```

### Prebuilt Binaries
##### Windows
- [0.1.0](https://github.com/Gunbard/ThumbThumb/releases/download/0.1.0/thumbthumb-0.1.0.zip)

### License
MIT