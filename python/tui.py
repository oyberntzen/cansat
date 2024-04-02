import pytermgui as ptg

class Option:
    def __init__(self, options, x, y):
        self.options = options
        self.x = x
        self.y = y

        self.selected = 0

    def draw(self):
        for i, option in enumerate(self.options):
            cursor = ">" if i == self.selected else " "
            ptg.print_to((self.x, self.y+i), f"{cursor} {str(option)}")

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

class ChoiceField:
    def __init__(self, choices):
        self.choices = choices
        self.selected = 0

    def __str__(self):
        return str(self.choices[self.selected])

    def update(self, key):
        if key == "f":
            self.selected = (self.selected+1) % len(self.choices)
            return True
        return False

class NumberField:
    def __init__(self):
        self.num = 0

    def __str__(self):
        return str(self.num)

    def update(self, key):
        if key == "f":
            self.num = 0
            return True
        if key.isdigit():
            digit = int(key)
            self.num *= 10
            self.num += digit
            return True
        return False

QUIT = 0
CHANGE_SESSION = 1
PLOT_VARIABLE = 2
CHANGED = 3

class TUI:
    def __init__(self, sessions, variables):
        self.packet_pos = (0, 1)
        self.sessions_pos = (30, 1)
        self.plot_pos = (60, 1)
        self.options_pos = (80, 1)
        self.options_spacing = 15

        self.session_option = Option(sessions, self.sessions_pos[0], self.sessions_pos[1]) 

        self.num_dimensions = ChoiceField(["2D", "3D"])
        self.plot_start_choice = ChoiceField(["From:", "Last:"])
        self.plot_start_num = NumberField()
        self.plot_option = Option([self.num_dimensions, self.plot_start_choice, self.plot_start_num], self.plot_pos[0], self.plot_pos[1])

        self.dimensions_option = []
        max_dimensions = 3
        for i in range(max_dimensions):
            self.dimensions_option.append(Option(variables, self.options_pos[0]+self.options_spacing*i, self.options_pos[1]))

        self.options = [self.session_option] + [self.plot_option] + self.dimensions_option
        self.current_option = 0

        self.variables = variables

        ptg.hide_cursor()
        self.draw([])

    def update(self):
        key = ptg.getch()
        message = None
        changed = True

        if key == "q":
            ptg.show_cursor()
            message = (QUIT, None)
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

            num_dimensions = self.num_dimensions.selected+2
            if self.current_option == num_dimensions+2:
                self.current_option = 1
                variables = []
                for i in range(num_dimensions):
                    variables.append(self.dimensions_option[i].selected_option())
                message = (PLOT_VARIABLE, variables)

        else:
            selected = self.options[self.current_option].selected_option()
            if hasattr(selected, "update"):
                changed = selected.update(key)
            else:
                changed = False

        if changed and message == None:
            message = (CHANGED, None)

        return message

    def draw(self, packets):
        ptg.clear()
        for i in range(self.current_option+1):
            self.options[i].draw()
        #ptg.print_to(self.packet_pos, self.packet)

        if len(packets) > 0:
            for i, variable in enumerate(self.variables):
                value = variable.value(packets)
                if type(value) == float:
                    value = round(value, 4)
                ptg.print_to((self.packet_pos[0], self.packet_pos[1]+i), f"{variable.name}: {value}")

    def change_sessions(self, new_sessions):
        self.options[0].change_options(new_sessions)

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