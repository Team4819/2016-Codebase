import yeti


class DeadAuto(yeti.Module):

    def module_init(self):
        self.debug.set_code((False, False, False), "disabled")
