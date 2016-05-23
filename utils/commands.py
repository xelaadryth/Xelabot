import traceback


class Commands:
    def __init__(self, exact_match_commands=None, starts_with_commands=None):
        if exact_match_commands is None:
            self.exact_match_commands = {}
        else:
            self.exact_match_commands = exact_match_commands
        if starts_with_commands is None:
            self.starts_with_commands = {}
        else:
            self.starts_with_commands = starts_with_commands

    def execute_command(self, command, **kwargs):
        """
        Given a command, try to execute it if it matches any of the given patterns.
        :param command: The section of a message to check the dictionary for
        :return: bool - True if a command was executed, false otherwise
        """
        executed = False

        command = command.lower()

        if 'command' not in kwargs:
            kwargs['command'] = command

        try:
            if command in self.exact_match_commands:
                self.exact_match_commands[command](**kwargs)
                executed = True

            for prefix, callback in self.starts_with_commands.items():
                if command.startswith(prefix):
                    callback(**kwargs)
                    executed = True
        except Exception as e:
            print('Error executing command {}: {}'.format(command, repr(e)))
            traceback.print_exc()

        return executed
