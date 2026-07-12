# ui/ui_state.py

from dataclasses import dataclass
from enum import Enum

class UITab(Enum):
    OVERVIEW = "overview"
    BUILDINGS = "buildings"
    INVENTORIES = "inventories"
    TRANSPORT = "transport"
    WORKERS = "workers"
    CONTRACTS = "contracts"

@dataclass
class UIState:
     info_tab_options: list[InfoTab] = field(default_factory=lambda: [
        UITab.OVERVIEW,
        UITab.BUILDINGS,
        UITab.INVENTORIES,
        UITab.TRANSPORT,
        UITab.WORKERS,
        UITab.CONTRACTS,
    ])

    info_tab_idx: int = 0
    selected_contract_id: int | None = None

    @property
    def current_info_tab(self) -> str:
        return self.info_tab_options[self.info_tab_idx]

    def next_info_tab(self) -> None:
        self.info_tab_idx = (self.info_tab_idx + 1) % len(self.info_tab_options)

    def previous_info_tab(self) -> None:
        self.info_tab_idx = (self.info_tab_idx - 1) % len(self.info_tab_options)
