import os, sys, django

#setting up django workspace (something that normally manage.py would do)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bit4All.settings')
django.setup()

from PyQt5.QtWidgets import QApplication
from BitEx.views import loginWindow    #settings must be set before importing views


def main():

    #Inizializing the login interface
    app = QApplication(sys.argv)
    
    login_window = loginWindow()

    #Show the login App
    login_window.show() 

    app.exec_()

if __name__ == '__main__':
    main()


