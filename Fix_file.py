import os

def fix_password_folder():
    folder = "Password"
    if os.path.isdir(folder):
        return "OK"
    else:
        os.mkdir(folder)
        return "ERROR"