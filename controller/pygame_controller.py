import pygame
from model.ui_state import UITab


class PygameController:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.selected_building_type_key = "lumber_camp"
        self.make_building = False
        self.make_supply_link = False
        self.link_source_id = None
        self.link_dest_id = None
        self.delete_item = False

    def handle_event(self, event: pygame.event.Event, world, ui_state, view) -> None:


        if event.type == pygame.KEYDOWN:
            handled_contract_keydown = False
            if ui_state.current_info_tab == UITab.CONTRACTS:
                handled_contract_keydown = self._handle_contract_keydown(event, world, ui_state)

            if not handled_contract_keydown:
                self._handle_keydown(event, world, ui_state, view)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button(event, world)

    def _handle_keydown(self, event: pygame.event.Event, world, ui_state, view) -> None:

        building_types = world.config.building_types.values()
        if event.key == pygame.K_s:
            self.make_supply_link = True
        elif event.key == pygame.K_LEFTBRACKET:
            ui_state.previous_info_tab()
            if ui_state.info_tab_options[ui_state.info_tab_idx] != UITab.CONTRACTS:
                ui_state.deselect_contract_id()
        elif event.key == pygame.K_RIGHTBRACKET:
            ui_state.next_info_tab()
            if ui_state.info_tab_options[ui_state.info_tab_idx] != UITab.CONTRACTS:
                ui_state.deselect_contract_id()
        elif event.key == pygame.K_d:
            self.delete_item = True
        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
            world.increase_speed()
        elif event.key == pygame.K_MINUS:
            world.decrease_speed()

        else:
            for btype in building_types:
                if event.key == pygame.key.key_code(btype.key_code):
                    self.make_building = True
                    self.selected_building_type_key = btype.key

    def _handle_contract_keydown(self, event, world, ui_state):

        sorted_contract_ids = world.get_contract_ids_sorted_by_price()

        if event.key == pygame.K_DOWN:
            if ui_state.selected_contract_id is None:
                ui_state.selected_contract_id = sorted_contract_ids[0]
            else:
                cur_idx = sorted_contract_ids.index(ui_state.selected_contract_id)
                if cur_idx == len(sorted_contract_ids) - 1:
                    ui_state.selected_contract_id = sorted_contract_ids[0]
                else:
                    ui_state.selected_contract_id = sorted_contract_ids[cur_idx+1]

            return True
        if event.key == pygame.K_UP:
            if ui_state.selected_contract_id is None:
                ui_state.selected_contract_id = sorted_contract_ids[-1]
            else:
                cur_idx = sorted_contract_ids.index(ui_state.selected_contract_id)
                if cur_idx == 0:
                    ui_state.selected_contract_id = sorted_contract_ids[-1]
                else:
                    ui_state.selected_contract_id = sorted_contract_ids[cur_idx-1]

            return True

        if event.key == pygame.K_RIGHT:
            if ui_state.selected_contract_id is None:
                return False
            world.contracts[ui_state.selected_contract_id].increase_amount()
            return True
        if event.key == pygame.K_LEFT:
            if ui_state.selected_contract_id is None:
                return False
            world.contracts[ui_state.selected_contract_id].decrease_amount()
            return True

        return False
    def _handle_mouse_button(self, event: pygame.event.Event, world) -> None:
        if event.button != 1:
            return

        mouse_x, mouse_y = event.pos

        tile_x = mouse_x // self.tile_size
        tile_y = mouse_y // self.tile_size

        if not world.grid.is_inside(tile_x, tile_y):
            return

        if self.delete_item:
            del_id = world.grid.get_tile(tile_x, tile_y).building_id
            world.delete_building(del_id)
            self.delete_item = False

        elif self.make_supply_link:
            if self.link_source_id is None:
                self.link_source_id = world.grid.get_tile(tile_x, tile_y).building_id
                if self.link_source_id is None:
                    print ('No source building found!')
                    return
                print (f'Source building id = {self.link_source_id}')
            else:
                if self.link_dest_id is None:
                    self.link_dest_id =  world.grid.get_tile(tile_x, tile_y).building_id
                    if self.link_dest_id is None:
                        print ('No destination building found!')
                        return
                    print (f'Destination building id = {self.link_dest_id}')
            
                    source_bldg = world.buildings[self.link_source_id]
                    dest_bldg = world.buildings[self.link_dest_id]

                    # only items the source can hold AND the destination can accept
                    possible_items = {
                        key: limit for key, limit in source_bldg.inventory.limits.items()
                        if dest_bldg.inventory.accepts_item(key)
                    }

                    # do not take inputs from the source building
                    for key in source_bldg.recipe_keys:
                        for item in world.config.recipes[key].inputs.keys():
                            possible_items.pop(item, None)

                    item_key = None
                    # prioritize items the destination needs as a recipe input
                    for key in dest_bldg.recipe_keys:
                        for item in world.config.recipes[key].inputs.keys():
                            if item in possible_items:
                                item_key = item
                                break
                        if item_key is not None:
                            break

                    if item_key is None and possible_items:
                        item_key = next(iter(possible_items))

                    if item_key is None:
                        print ('WARNING item_key not found!')
                    else:
                        try:
                            world.add_supply_link(
                                source_building_id=self.link_source_id,
                                target_building_id=self.link_dest_id,
                                item_key=item_key,
                                required_workers=1,
                                amount_per_job=1,
                            )
                        except ValueError as error:
                            print(f"Could not create supply link: {error}")

                    self.make_supply_link = False
                    self.link_source_id = None
                    self.link_dest_id = None
        else:
            if self.make_building:
                try:
                    building_id = world.add_building(
                        self.selected_building_type_key,
                        tile_x,
                        tile_y,
                    )

                    print(
                        f"Added building {building_id}: "
                        f"{self.selected_building_type_key} at ({tile_x}, {tile_y})"
                    )

                    self.make_building = False


                except ValueError as error:
                    print(f"Could not place building: {error}")
