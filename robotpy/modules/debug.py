import yeti


class DebugModule(yeti.Module):

    def module_init(self):
        self.light_strings = self.engine.get_module("light_strings")
        self.light_strings_enabled = True

    def set_code(self, code=None, buffer="disabled"):
        if code is not None and self.light_strings_enabled:
            try:
                self.light_strings.set_debug_code(code, buffer)
            except:
                self.light_strings_enabled = False
