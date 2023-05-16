# Client

Heavily W.I.P. at the moment.


## Config

Create a file called `config.py` and fill it with the following values(relevant to you):

```
SITE_URL = "your-server.com"

```

## Releases
Check out the releases for pre-compiled binaries/installers of the client. Remember to edit the config.ini file before running. That will be done in the setup, but still.

## Manual compilationn
Compile the client like so.

Firstly, check if your Python version is => 3.11
```
$ python --version
> Python 3.11.3
``` 
Then, clone the repository.
`$ git clone https://github.com/confestim/custoMM` 
`$ cd custoMM/src/client`
If you don't have pyinstaller installed, do:
`$ pip install pyinstaller`
Once that's ready, you're ready to compile!
`$ python -m PyInstaller --onefile main.py --noconsole`

The exe file will reside in the newly created dist/ folder. Don't forget to copy the assets and the config to the same folder that your EXE resides(that means you will have to send them over to your friends along with the EXE file):
`cp assets ../config.ini dist`

From here, do whatever with the dist folder, I would recommend zipping it.
 

