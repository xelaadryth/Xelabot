import traceback


class CommandSet:
    def __init__(self, exact_match_commands=None, starts_with_commands=None, children=None):
        if exact_match_commands is None:
            self.exact_match_commands = {}
        else:
            self.exact_match_commands = exact_match_commands
        if starts_with_commands is None:
            self.starts_with_commands = {}
        else:
            self.starts_with_commands = starts_with_commands

        # Commands are executed on all children as well
        if children is None:
            self.children = set()
        else:
            self.children = children

    def execute_command(self, display_name, full_command):
        """
        Given a command, try to execute it if it matches any of the given patterns.
        :param display_name: str - The user executing the command
        :param full_command: str - The entire message
        """
        split_command = full_command.split(maxsplit=1)
        command = split_command[0].lower()
        params = split_command[1:]

        try:
            if command in self.exact_match_commands:
                self.exact_match_commands[command](display_name)

            if command in self.starts_with_commands:
                self.starts_with_commands[command](display_name, params)

            # Recursively run the commands of all children
            for child in self.children:
                child.execute_command(display_name, full_command)
        except Exception as e:
            print('Error executing command {}: {}'.format(command, repr(e)))
            traceback.print_exc()

    def add_commands(self, exact_match_commands=None, starts_with_commands=None):
        """
        Adds more commands to our definitions.
        :param exact_match_commands: dict<str, Function> - Commands that takes only display name as an argument
        :param starts_with_commands: dict<str, Function> - Commands that take the rest of the message as an argument
        """
        if exact_match_commands:
            self.exact_match_commands.update(exact_match_commands)
        if starts_with_commands:
            self.starts_with_commands.update(starts_with_commands)

    def has_command(self, full_command):
        """
        Given the trigger of a command, see if it is present.
        :param full_command: str - The entire message
        :return: bool - True if we have this command, False otherwise
        """
        command = full_command.split(maxsplit=1)[0].lower()
        return command in self.exact_match_commands or command in self.starts_with_commands

    def clear_children(self):
        """
        Remove all child command sets.
        """
        self.children = set()

    def add_command_set(self, child):
        """
        Add a child command set.
        :param child: Commands - A child command set to add to the current set
        """
        self.children.add(child)

    def remove_command_set(self, child):
        """
        Remove a child command set.
        :param child: Commands - A child command set to remove from the current set
        """
        self.children.discard(child)
