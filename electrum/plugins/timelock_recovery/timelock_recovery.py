from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from electrum.plugin import BasePlugin
from electrum.transaction import PartialTxInput

if TYPE_CHECKING:
    from electrum.gui.qt import ElectrumWindow
    from electrum.transaction import PartialTxOutput, PartialTransaction
    from electrum.wallet import Abstract_Wallet

class TimelockRecoveryContext:
    main_window: 'ElectrumWindow'
    wallet: 'Abstract_Wallet'
    wallet_name: str
    timelock_days: Optional[int]
    alert_address: Optional[str]
    cancellation_address: Optional[str]
    outputs: Optional[List['PartialTxOutput']]
    alert_tx: Optional['PartialTransaction']
    recovery_tx: Optional['PartialTransaction']
    cancellation_tx: Optional['PartialTransaction']
    recovery_plan_id: Optional[str]
    recovery_plan_created_at: Optional[datetime]

    def __init__(self, main_window: 'ElectrumWindow'):
        self.main_window = main_window
        self.wallet = main_window.wallet
        self.wallet_name = str(self.wallet)

    def _get_address_by_label(self, label: str) -> Optional[str]:
        unused_addresses = list(self.wallet.get_unused_addresses())
        for addr in unused_addresses:
            if self.wallet.get_label_for_address(addr) == label:
                return addr
        for addr in unused_addresses:
            if not self.wallet.is_address_reserved(addr) and not self.wallet.get_label_for_address(addr):
                self.wallet.set_label(addr, label)
                return addr
        if self.wallet.is_deterministic():
            addr = self.wallet.create_new_address(False)
            self.wallet.set_label(addr, label)
            return addr
        return None

    def get_address_by_label(self, label: str) -> Optional[str]:
        addr = self._get_address_by_label(label)
        if addr:
            self.wallet.set_reserved_state_of_address(addr, reserved=True)
        return addr

class PartialTxInputWithFixedNsequence(PartialTxInput):
    _fixed_nsequence: int

    def __init__(self, *args, nsequence: int = 0xfffffffe, **kwargs):
        self._fixed_nsequence = nsequence
        super().__init__(*args, **kwargs)

    @property
    def nsequence(self) -> int:
        return self._fixed_nsequence

    @nsequence.setter
    def nsequence(self, value: int):
        pass # ignore override attempts

class TimelockRecoveryPlugin(BasePlugin):
    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
