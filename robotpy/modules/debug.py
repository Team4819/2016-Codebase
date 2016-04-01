import yeti


class DebugModule(yeti.Module):

    def module_init(self):
        self.light_strings = self.engine.get_module("light_strings")
        self.light_strings_enabled = True
        self.auto_step_count = 1

    def set_code(self, code=None, buffer="disabled"):
        if code is not None and self.light_strings_enabled:
            try:
                self.light_strings.set_debug_code(code, buffer)
            except:
                self.light_strings_enabled = False

    def set_auto_steps(self, count):
        self.auto_step_count = count
        self.set_auto_progress(-1)

    def set_auto_progress(self, step):
        self.set_code([i <= step for i in range(self.auto_step_count)], "auto")