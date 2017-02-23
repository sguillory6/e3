import mimetypes
import os
import random
import re

from bitbucket.common.WeightedRandomGenerator import weighted_choice

from bitbucket.common.RandomWords import RandomWords


class CodeEditor:
    """
    Pseudo random file editor
    """
    def __init__(self, files):
        self.files = files
        self.add_modify_delete = [20, 60, 20]
        self.lines_add_modify_remove = [30, 50, 20]
        self.words = RandomWords()
        self.expression = re.compile(r"^(\s*)(.*)$")

    def randomly_edit_files(self, min_files_to_edit, max_files_to_edit, min_lines_to_change, max_lines_to_change):
        """
        Edit some files in a repository
        :param min_files_to_edit: The min number of files to add/modify/delete
        :param max_files_to_edit: The max number of files to add/modify/delete
        :param min_lines_to_change: The min number of lines to add/modify/delete
        :param max_lines_to_change: The max number of lines to add/modify/delete
        :return: a list of files that were added/modified/deleted
        :rtype: list(str)
        """
        files_changed = []
        no_files_to_change = random.randint(min_files_to_edit, max_files_to_edit)
        no_lines_to_change = random.randint(min_lines_to_change, max_lines_to_change)

        for idx in range(0, no_files_to_change - 1):
            if len(self.files) == 0:
                # Exhausted the number of files in the repo
                break
            pos = random.randint(0, len(self.files)-1)
            file_to_edit = self.files[pos]
            del(self.files[pos])

            action = weighted_choice(self.add_modify_delete)
            if action == 0:
                # Add new file
                files_changed.append(self._add_new_file(os.path.dirname(file_to_edit), no_lines_to_change))

            elif action == 1:
                # Modify existing file
                files_changed.append(self._modify_existing_file(file_to_edit, no_lines_to_change))

            elif action == 2:
                # Delete exiting file
                files_changed.append(self._delete_existing_file(file_to_edit))

        return files_changed

    def _add_new_file(self, destination, no_lines):
        new_file = os.path.join(destination, self.words.random_word() + u".txt")
        with open(new_file, "w") as f:
            lines = []
            for line in range(0, no_lines):
                lines.append(self.words.random_sentence(random.randint(4, 16)))
            f.write("\n".join(lines))
        return new_file

    @staticmethod
    def _delete_existing_file(file_to_delete):
        os.unlink(file_to_delete)
        return file_to_delete

    def _modify_existing_file(self, file_to_edit, no_lines_to_change):
        with open(file_to_edit, "r") as src:
            lines = src.read().splitlines()

            no_of_lines_in_file = len(lines)
            if no_lines_to_change > no_of_lines_in_file:
                no_lines_to_change = no_of_lines_in_file

            changes = 0
            while changes < no_lines_to_change:
                # Choose the line to work on
                idx = random.randint(0, len(lines) - 1)
                # Choose what do do to the line
                action = weighted_choice(self.lines_add_modify_remove)
                if action == 0:
                    # Add
                    lines.insert(idx, self.words.random_sentence(random.randint(4, 16)))

                elif action == 1:
                    # Modify
                    lines[idx] = self._modify_exiting_line(lines[idx])

                elif action == 2:
                    # Delete
                    del(lines[idx])

                # Move to next line
                changes += 1

            if lines:
                with open(file_to_edit, "w") as save_src:
                    # Write the changes to disk
                    save_src.write("\n".join(lines))

        return file_to_edit

    def _modify_exiting_line(self, line):
        ws, line_content = self._split_starting_whitespace(line)
        updated_line = "%s %s" % (line_content, self.words.random_sentence(random.randint(4, 6)))
        updated_line = updated_line.split(' ')
        random.shuffle(updated_line)
        return "%s%s" % (ws, ' '.join(updated_line))

    def _split_starting_whitespace(self, line):
        m = self.expression.match(line)
        if m:
            ws = m.group(1)
            line_content = m.group(2)
        else:
            ws = ''
            line_content = line
        return ws, line_content

    @classmethod
    def from_repository(cls, repository_dir):
        results = []
        for root, dirs, files in os.walk(repository_dir, followlinks=False):
            for name in files:
                full_path = os.path.join(root, name)
                mime_type, _ = mimetypes.guess_type(full_path)
                if mime_type and mime_type.startswith("text/"):
                    results.append(full_path)
            if ".git" in dirs:
                dirs.remove(".git")
        return cls(results)

    @classmethod
    def from_file(cls, code_file):
        with open(code_file, "r") as f:
            files = f.read().splitlines()
        return cls(files)
