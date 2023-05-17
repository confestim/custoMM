import pystray
from PIL import Image
import sys, os
from time import sleep

class Notify():
	
    def __init__(self, base_dir, exit_after=False):
        """Standalone notification module

        Args:
            base_dir (os.path): base dir of application
            exit_after (bool, optional): Specify if you want to exit after a notif. Defaults to False.
        """
        self.exit_after = exit_after

        image = Image.open(os.path.join(base_dir, os.path.join("assets", "icon.png")))
        
        # Singular menu option
        self.menu =  pystray.Menu(
            pystray.MenuItem(
                "Exit", self.quit
            )
        )

        self.icon = pystray.Icon(
            "name", image, "CustoMM", self.menu)
        
        self.icon.run_detached()
        
        self.notified = False
        self.exit = False

    def notification(self, message:str):
        """Notification method

        Args:
            message (str): Message you want to send
        """
        sleep(2)
        # Not
        if not self.notified:
            self.icon.notify(message, title="custoMM")
        if self.exit_after:
            self.quit()

    def quit(self):
        self.exit = True
        self.icon.stop()
    