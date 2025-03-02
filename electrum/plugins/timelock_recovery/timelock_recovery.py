from electrum.plugin import BasePlugin

class TimelockRecoveryPlugin(BasePlugin):
    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
