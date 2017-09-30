import sublime
import sublime_plugin

try:
    from .json_pretty import json_pretty
except ValueError:
    from json_pretty import json_pretty

class JsonPrettyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        regions = view.sel()
        try:
            if len(regions) > 1 or not regions[0].empty():
                for region in view.sel():
                    if not region.empty():
                        s = view.substr(region)
                        s = json_pretty(s)
                        view.replace(edit, region, s)
            else:  # format all text
                alltextreg = sublime.Region(0, view.size())
                s = view.substr(alltextreg)
                s = json_pretty(s)
                view.replace(edit, alltextreg, s)
        except:
            sublime.active_window().status_message('errors perhaps json syntax error')