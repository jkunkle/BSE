from model.world import World
from utils.content_loader import load_config


from system.production_system import ProductionSystem
from system.transport_system import TransportSystem

BUILDINGS_DATA = 'data/buildings.json'
RECIPES_DATA = 'data/recipes.json'
ITEMS_DATA = 'data/items.json'

import pygame
from pathlib import Path

from model.grid import Grid
from model.world import World
from view.pygame_view import PygameView
from controller.pygame_controller import PygameController


import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s",
)


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("BuildSupply Prototype")

    clock = pygame.time.Clock()

    cstore = load_config(BUILDINGS_DATA, RECIPES_DATA, ITEMS_DATA)

    world = World(cstore, workers=0)
    uistate = UIState()

    #id_lumber = world.add_building('lumber_camp', 5, 5)
    #id_sawmill = world.add_building('sawmill', 20, 20)

    #world.add_supply_link(
    #    source_building_id=id_lumber,
    #    target_building_id=id_sawmill,
    #    item_key="wood",
    #    workers=1,
    #    amount_per_job=1,
    #) 


    view = PygameView(tile_size=20)
    controller = PygameController(tile_size=20)
    ps = ProductionSystem()
    ts = TransportSystem()

    fixed_dt = 0.1
    accumulator = 0.0

    running = True

    while running:
        frame_dt = clock.tick(60) / world.speed
        accumulator += frame_dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                controller.handle_event(event, world, view)

        while accumulator >= fixed_dt:
            step(world, ps, ts, frame_dt)
            accumulator -= fixed_dt

        view.draw(screen, world)

        pygame.display.flip()

    pygame.quit()

def step(world, ps, ts, dt):

    world.advance_time(dt)

    ps.update(world, dt)

    ts.update(world, dt)



if __name__ == "__main__":
    main()

#def main():
#
#    cstore = load_config(BUILDINGS_DATA, RECIPES_DATA)
#
#    world = World(cstore, workers=10)
#
#    id_lumber = world.add_building('lumber_camp', 5, 5)
#    id_sawmill = world.add_building('sawmill', 10, 10)
#
#    world.add_supply_link(
#        source_building_id=id_lumber,
#        target_building_id=id_sawmill,
#        item_key="wood",
#        workers=1,
#        amount_per_job=1,
#    ) 
#
#    run(world)
#
#
#def run(world):
#
#    ps = ProductionSystem()
#    ts = TransportSystem()
#    for i in range(0, 10):
#        step(world,ps, ts, 1)
#        print (world.transport_jobs)
#        print (world.buildings)
#
#        for b in world.buildings:
#            print (b)
#



