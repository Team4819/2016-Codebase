import yeti


class RockAuto(yeti.Module):

    def module_init(self):
        pass

    def get_led_code(self):
        return True, False, False, False
