from view.app import App
from cmm import Cmm

if __name__ == '__main__':
    Cmm.trace(lambda: App().run())
