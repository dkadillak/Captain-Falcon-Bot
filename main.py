import melee
import sys

def run_ai():
    '''
    Responsible for starting the emulation of melee using dolphin
    Expects human player to be using port 2, the AI taking port 1

    :return:
    '''
    console = melee.console.Console(path=r"C:\Users\Devin Kadillak\AppData\Roaming\Slippi Launcher\netplay",
                            is_dolphin=True,
                            slippi_address="127.0.0.1")

    controller = melee.controller.Controller(console=console,
                                  port=1,
                                  type=melee.ControllerType.STANDARD)

    controller_human = melee.controller.Controller(console=console,
                                        port=2,
                                        type=melee.ControllerType.GCN_ADAPTER)

    console.run(iso_path=r"C:\Users\Devin Kadillak\Documents\FM-Slippi\melee_v1.02.iso")



    # onnect to the console
    print("Connecting to console...")
    if not console.connect():
        print("ERROR: Failed to connect to the console.")
        sys.exit(-1)
    print("Console connected")

    # connect AI controller
    print("Connecting controller to console...")
    if not controller.connect():
        print("ERROR: Failed to connect the controller.")
        sys.exit(-1)
    print("AI Controller connected")

    # connect human controller
    print("Connecting human controller to console...")
    if not controller_human.connect():
        print("ERROR: Failed to connect the controller.")
        sys.exit(-1)
    print("Human Controller connected")

    #frameData = melee.framedata.FrameData()

    while True:

        # get all the data associated with the current frame we are in
        gamestate = console.step()

        if gamestate is None:
            print('none')
            continue

        # logic for how AI should behave
        if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            short_hop_fair(gamestate.players[1], controller)
            '''
            if ready_to_attack(gamestate.players[1], gamestate.players[2], gamestate, frameData, controller):
                short_hop_fair(gamestate.players[1], controller)
            else:
                move_to_attack(gamestate.players[1], gamestate.players[2], controller)
            '''
        else:
            print('menu helper')
            # using libmelee's menuhelper to get us in a game
            melee.menuhelper.MenuHelper.menu_helper_simple(gamestate=gamestate,
                                                controller=controller,
                                                character_selected=melee.Character.CPTFALCON,
                                                costume=3,
                                                stage_selected=melee.Stage.FINAL_DESTINATION,
                                                connect_code="",
                                                autostart=True,
                                                swag=False)


def move_to_attack(ai_state, player_state, controller):
    '''
    moves the ai player towards the Human Player

    :param ai_state: PlayerState object representing the AI player
    :param player_state: PlayerState object representing the human player
    :param controller: Controller object which controls the AI player
    :return: None
    '''

    # move ai right if ai is left of human player
    if ai_state.position.x < player_state.position.x:
        controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
        controller.flush()

    else:
        # move ai left if ai is right of human player
        controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
        controller.flush()


def ready_to_attack(ai_state, player_state, gamestate, frameData, controller):
    '''
    Determines if the AI player is within attacking range of the Human Player
    :param ai_state: PlayerState object representing the AI player
    :param player_state: PlayerState object representing the human player
    :param gamestate: GameState object, a snapshot of the current frame in the game
    :param frameData: FrameData object, Helper functions to be able to query Melee frame data in a way useful to bots
    :param controller: Controller object which controls the AI player
    :return: Boolean
    '''

    if frameData.in_range(ai_state, player_state, gamestate.stage):
        controller.release_all()
        return True

    else:
        return False


def short_hop_fair(ai_state, controller):
    '''
    Makes the AI do a short hop forward air attack, fast falls the move on frame 13 of the fair animation, and L cancels 3 frames later
    :param ai_state: PlayerState object representing the AI player
    :param controller: Controller object controlling the AI player
    :return: None
    '''

    controller.release_all()

    # make cap jump
    if ai_state.action == melee.enums.Action.STANDING:
        controller.press_button(melee.enums.Button.BUTTON_Y)
        controller.flush()

    # release jump button on knee bend animation so it's a short hop
    elif ai_state.action == melee.enums.Action.KNEE_BEND:
        controller.release_all()

    elif ai_state.action == melee.enums.Action.JUMPING_FORWARD:
        # once cap is in the air, throw out a fair as soon as possible
        if ai_state.action_frame == 5:
            controller.release_all()
            controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
            controller.flush()

    elif ai_state.action == melee.enums.Action.FAIR:
        # fast fall the fair a frames before the active hitbox frame
        if ai_state.action_frame == 13:
            controller.release_all()
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.5, 0)
            controller.flush()

        # L-Cancel within 7 frames of landing
        if ai_state.action_frame >= 16:
            controller.press_shoulder(melee.enums.Button.BUTTON_L, 1)
            controller.flush()

def read_slp():
    '''
    Function to read .slp files
    :return:
    '''
    console = melee.Console(is_dolphin=False,
                            allow_old_version=False,
                            path=r"C:\Users\Devin Kadillak\Documents\Slippi\Game_20201203T001807.slp"
                            )
    console.connect()

    while True:
        gamestate = console.step()
        # step() returns None when the file ends
        if gamestate is None:
            break
        print("Frame " + str(gamestate.frame))
        for _, player in gamestate.players.items():
            print("\t", player.stock, player.percent)


# Main
if __name__ == '__main__':
    run_ai()

