import os

# Helper script for remote development

if __name__=="__main__":
    os.system("sudo systemctl restart light")
    os.system("sudo journalctl -fu light")