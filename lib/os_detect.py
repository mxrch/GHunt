from platform import system, uname


class Os:
    """
    returns class with properties:
    .cygwin   Cygwin detected
    .wsl      Windows Subsystem for Linux (WSL) detected
    .mac      Mac OS detected
    .linux    Linux detected
    .bsd      BSD detected
    """

    def __init__(self):
        syst = system().lower()

        # initialize
        self.cygwin = False
        self.wsl = False
        self.mac = False
        self.linux = False
        self.windows = False
        self.bsd = False

        if 'cygwin' in syst:
            self.cygwin = True
            self.os = 'cygwin'
        elif 'darwin' in syst:
            self.mac = True
            self.os = 'mac'
        elif 'linux' in syst:
            self.linux = True
            self.os = 'linux'
            if 'Microsoft' in uname().release:
                self.wsl = True
                self.linux = False
                self.os = 'wsl'
        elif 'windows' in syst:
            self.windows = True
            self.os = 'windows'
        elif 'bsd' in syst:
            self.bsd = True
            self.os = 'bsd'

    def __str__(self):
        return self.os
