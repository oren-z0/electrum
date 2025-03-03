from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from electrum.plugin import BasePlugin
from electrum.transaction import PartialTxInput

if TYPE_CHECKING:
    from electrum.gui.qt import ElectrumWindow
    from electrum.transaction import PartialTxOutput, PartialTransaction
    from electrum.wallet import Abstract_Wallet

ALERT_ADDRESS_LABEL = "Timelock Recovery Alert Address"
CANCELLATION_ADDRESS_LABEL = "Timelock Recovery Cancellation Address"

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

class TimelockRecoveryContext:
    main_window: 'ElectrumWindow'
    wallet: 'Abstract_Wallet'
    wallet_name: str
    timelock_days: Optional[int] = None
    cancellation_address: Optional[str] = None
    outputs: Optional[List['PartialTxOutput']] = None
    alert_tx: Optional['PartialTransaction'] = None
    recovery_tx: Optional['PartialTransaction'] = None
    cancellation_tx: Optional['PartialTransaction'] = None
    recovery_plan_id: Optional[str] = None
    recovery_plan_created_at: Optional[datetime] = None
    _alert_address: Optional[str] = None
    _cancellation_address: Optional[str] = None

    def __init__(self, main_window: 'ElectrumWindow'):
        self.main_window = main_window
        self.wallet = main_window.wallet
        self.wallet_name = str(self.wallet)

    def _get_address_by_label(self, label: str) -> str:
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
            if addr:
                self.wallet.set_label(addr, label)
                return addr
        return ''

    def get_alert_address(self) -> str:
        if self._alert_address is None:
            self._alert_address = self._get_address_by_label(ALERT_ADDRESS_LABEL)
        return self._alert_address

    def get_cancellation_address(self) -> str:
        if self._cancellation_address is None:
            self._cancellation_address = self._get_address_by_label(CANCELLATION_ADDRESS_LABEL)
        return self._cancellation_address

class TimelockRecoveryPlugin(BasePlugin):
    def __init__(self, parent, config, name):
        BasePlugin.__init__(self, parent, config, name)
