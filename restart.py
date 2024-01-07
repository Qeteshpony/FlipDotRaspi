import os

# Helper script for remote development

if __name__=="__main__":
    os.system("sudo systemctl restart flipdot")
    os.system("sudo journalctl -fu flipdot")