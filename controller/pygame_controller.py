import pygame


class PygameController:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.selected_building_type_key = "lumber_camp"
        self.make_building = False
        self.make_supply_link = False
        self.link_source_id = None
        self.link_dest_id = None
        self.delete_item = False

    def handle_event(self, event: pygame.event.Event, world, view) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event, world, view)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button(event, world)

    def _handle_keydown(self, event: pygame.event.Event, world, view) -> None:

        building_types = world.config.building_types.values()
        if event.key == pygame.K_s:
            self.make_supply_link = True
        elif event.key == pygame.K_LEFTBRACKET:
            view.advance_info_tab(left=True)
        elif event.key == pygame.K_RIGHTBRACKET:
            view.advance_info_tab(left=False)
        elif event.key in [pygame.K_DOWN,pygame.K_UP,pygame.K_RIGHT,pygame.K_LEFT]:
            if view.info_tab_options[view.info_tab_idx] == 'contracts':
                if event.key == pygame.K_DOWN:
                    world.try_contract_list_down()
                if event.key == pygame.K_UP:
                    world.try_contract_list_up()
                if event.key == pygame.K_RIGHT:
                    world.try_current_contract_increase()
                if event.key == pygame.K_LEFT:
                    world.try_current_contract_decrease()
        elif event.key == pygame.K_UP:
            view.process_up_key()
        elif event.key == pygame.K_RIGHT:
            view.process_right_key()
        elif event.key == pygame.K_LEFT:
            view.process_left_key()
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

                    # get all possible items stored
                    possible_items = dict(world.buildings[self.link_source_id].inventory.limits)

                    # do not take inputs from the source building
                    for key in source_bldg.recipe_keys:
                        for item in world.config.recipes[key].inputs.keys():
                            possible_items.pop(item)

                    item_key = None
                    # prioritize inputs to dest building
                    for key in dest_bldg.recipe_keys:
                        if key in possible_items:
                            item_key = key
                     
                    if item_key is None:
                        item_key = list(possible_items.keys())[0]

                    if item_key is None:
                        print ('WARNING item_key not found!')
                        return

                    world.add_supply_link(
                        source_building_id=self.link_source_id,
                        target_building_id=self.link_dest_id,
                        item_key=item_key,
                        required_workers=1,
                        amount_per_job=1,
                    ) 

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
