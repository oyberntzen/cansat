import pytermgui as ptg
import inspect

class Option:
    def __init__(self, options, x, y):
        self.options = options
        self.x = x
        self.y = y

        self.selected = 0

    def draw(self):
        for i, option in enumerate(self.options):
            cursor = ">" if i == self.selected else " "
            ptg.print_to((self.x, self.y+i+1), f"{cursor} {str(option)}")

    def move(self, offset):
        self.selected = (self.selected + offset) % len(self.options)

    def selected_option(self):
        return self.options[self.selected]

    def change_options(self, new_options):
        new_selected = 0
        if len(self.options) != 0:
            for i, option in enumerate(new_options):
                if option == self.options[self.selected]:
                    new_selected = i
                    break
        self.selected = new_selected
        self.options = new_options

QUIT = 0
CHANGE_SESSION = 1
PLOT_VARIABLE = 2

class TUI:
    def __init__(self, sessions, variables, dimensions, packet):
        self.packet_pos = (0, 0)
        self.sessions_pos = (40, 0)
        self.options_pos = (80, 0)
        self.options_spacing = 15

        self.dimensions = dimensions

        self.options = [Option(sessions, self.sessions_pos[0], self.sessions_pos[1])]
        for i in range(self.dimensions):
            self.options.append(Option(variables, self.options_pos[0]+self.options_spacing*i, self.options_pos[1]))
        self.current_option = 0

        self.packet = packet


        ptg.hide_cursor()
        self.draw()

    def update(self):
        key = ptg.getch()
        changed = True
        message = None

        if key == "q":
            ptg.show_cursor()
            message = (QUIT, None)
            changed = False
        elif key == "w":
            self.options[self.current_option].move(-1)
        elif key == "s":
            self.options[self.current_option].move(1)
        elif key == "a":
            self.current_option = max(self.current_option-1, 0)
        elif key == "d":
            self.current_option += 1
            if self.current_option == 1:
                new_session = self.options[0].selected_option()
                message = (CHANGE_SESSION, new_session)
            elif self.current_option == len(self.options):
                self.current_option = 1
                variables = []
                for i in range(self.dimensions):
                    variables.append(self.options[i+1].selected_option())
                message = (PLOT_VARIABLE, variables)
        else:
            changed = False

        if changed:
            self.draw()

        return message

    def draw(self):
        ptg.clear()
        for i in range(self.current_option+1):
            self.options[i].draw()
        ptg.print_to(self.packet_pos, self.packet)

    def change_sessions(self, new_sessions):
        self.options[0].change_options(new_sessions)
        self.draw()

    def change_packet(self, new_packet):
        self.packet = new_packet
        self.draw()

if __name__ == "__main__":
    import time
    tui = TUI(["session1", "session2", "session2"], ["time", "temp", "humid"], 2)
    while True:
        message = tui.update()
        if message != None:
            flag, data = message
            if flag == QUIT:
                break
            print(flag, data)
        time.sleep(1/60)