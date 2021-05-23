import os
if 'nt' in os.name:
    os.system('./src/Libaries.bat')
else:
    os.system('sudo bash ./src/Libraries.sh')