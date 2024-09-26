How to install:   
Click code > download zip   
Extract the zip file, it does not matter where to.  

How to run:   
If on windows, run the application in the windows binary > satellite tracker folder   
If on linux, run the application in the linux binary > satellite tracker folder   

Currently I have an issue where each time the program is run, it needs to refresh all the files, which makes it reset the prefs.json folder on each launch and take longer to launch because it needs to download the ui files from the github repo. This is because of pyinstaller putting the program into a temporary directory each time it is run which is wiped after it is closed.   
   
   

If you want to run the python file directly (preferred as of right now):   
Run the install dependencies.bat file if on windows, or the install dependencies.sh file if on linux   
On linux before you can run the install dependencies.sh file you might need to right click on it, go to permissions, check the box that says "Allow executing the file as program," click save if applicable, and close the properties window.   
Run satellite tracker.py

MAC SUPPORT IS NOT GUARANTEED, I DO NOT HAVE ANYTHING THAT RUNS MACOS TO TEST THIS ON