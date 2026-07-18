# ui/ui_state.py

from dataclasses import dataclass, field
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

    pending_link_source_id: int | None = None
    pending_link_dest_id: int | None = None
    pending_link_item_choices: list[str] = field(default_factory=list)

    @property
    def current_info_tab(self) -> str:
        return self.info_tab_options[self.info_tab_idx]

    @property
    def choosing_link_item(self) -> bool:
        return bool(self.pending_link_item_choices)

    def next_info_tab(self) -> None:
        self.info_tab_idx = (self.info_tab_idx + 1) % len(self.info_tab_options)

    def previous_info_tab(self) -> None:
        self.info_tab_idx = (self.info_tab_idx - 1) % len(self.info_tab_options)

    def deselect_contract_id(self) -> None:
        self.selected_contract_id = None

    def start_link_item_choice(self, source_id: int, dest_id: int, item_choices: list[str]) -> None:
        self.pending_link_source_id = source_id
        self.pending_link_dest_id = dest_id
        self.pending_link_item_choices = item_choices

    def clear_link_item_choice(self) -> None:
        self.pending_link_source_id = None
        self.pending_link_dest_id = None
        self.pending_link_item_choices = []
