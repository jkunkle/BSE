import pygame


class PygameController:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.selected_building_type_key = "lumber_camp"
        self.make_supply_link = False
        self.link_source_id = None
        self.link_dest_id = None

    def handle_event(self, event: pygame.event.Event, world) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button(event, world)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_1:
            self.selected_building_type_key = "lumber_camp"
            print("Selected lumber_camp")

        elif event.key == pygame.K_2:
            self.selected_building_type_key = "sawmill"
            print("Selected sawmill")

        elif event.key == pygame.K_3:
            self.selected_building_type_key = "warehouse"
            print("Selected warehouse")

        elif event.key == pygame.K_s:
            self.make_supply_link = True
            print("Selected make supply link")

    def _handle_mouse_button(self, event: pygame.event.Event, world) -> None:
        if event.button != 1:
            return

        mouse_x, mouse_y = event.pos

        tile_x = mouse_x // self.tile_size
        tile_y = mouse_y // self.tile_size

        if not world.grid.is_inside(tile_x, tile_y):
            return

        if self.make_supply_link:
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
            
                    world.add_supply_link(
                        source_building_id=self.link_source_id,
                        target_building_id=self.link_dest_id,
                        item_key="wood",
                        required_workers=1,
                        amount_per_job=1,
                    ) 

                    self.make_supply_link = False
                    self.link_source_id = None
                    self.link_dest_id = None
        else:

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

            except ValueError as error:
                print(f"Could not place building: {error}")
