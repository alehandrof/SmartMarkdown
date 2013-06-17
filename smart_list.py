"""Smart list is used to automatially continue the current list."""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re

import sublime
import sublime_plugin


ORDER_LIST_PATTERN = re.compile(r"(\s*[(]?)(\d+)([.)]\s+)\S+")
UNORDER_LIST_PATTERN = re.compile(r"(\s*[-+\**]+)(\s+)\S+")
EMPTY_LIST_PATTERN = re.compile(r"(\s*)([-+\**]|[(]?\d+[.)])(\s+)$")
NONLIST_PATTERN = re.compile(r"(\s*[>|%]+)(\s+)\S?")


class SmartListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            # the content before point at the current line.
            before_point_region = sublime.Region(line_region.a,
                                                 region.a)
            before_point_content = self.view.substr(before_point_region)

            # Disable smart list when folded.
            folded = False
            for i in self.view.folded_regions():
                if i.contains(before_point_region):
                    self.view.insert(edit, region.a, '\n')
                    folded = True
            if folded:
                break

            match = EMPTY_LIST_PATTERN.match(before_point_content)
            if match:
                settings = sublime.load_settings("SmartMarkdown.sublime-settings")
                if settings.get("empty_list_bullet"):
                    insert_text = match.group(1) + \
                                  re.sub(r'\S', ' ', str(match.group(2))) + \
                                  match.group(3)
                    self.view.erase(edit, before_point_region)
                    self.view.insert(edit, line_region.a, insert_text)
                else:
                    self.view.erase(edit, before_point_region)
                break

            match = ORDER_LIST_PATTERN.match(before_point_content)
            if match:
                insert_text = match.group(1) + \
                              str(int(match.group(2)) + 1) + \
                              match.group(3)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            match = UNORDER_LIST_PATTERN.match(before_point_content)
            if match:
                insert_text = match.group(1) + match.group(2)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            match = NONLIST_PATTERN.match(before_point_content)
            if match:
                current_line = self.view.line(region.a)
                prev_line = self.view.line(current_line.a - 1)
                empty_nonlist = match.group(1) + match.group(2)
                if (self.view.substr(prev_line) == empty_nonlist) and (self.view.substr(current_line) == empty_nonlist):
                    self.view.replace(edit, current_line, '')
                    self.view.replace(edit, prev_line, '')
                else:
                    insert_text = match.group(1) + match.group(2)
                    self.view.insert(edit, region.a, "\n" + insert_text)
                break

            self.view.insert(edit, region.a, '\n')
        self.adjust_view()

    def adjust_view(self):
        for region in self.view.sel():
            self.view.show(region)
