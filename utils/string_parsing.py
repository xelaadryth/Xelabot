def list_to_string(word_list, join_word='and', prefix='', empty_word='no one'):
    """
    Given a list of strings, join them intelligently.
    :param word_list: list<str> - Words to join
    :param join_word: str - The word used to join the list together
    :param prefix: str - The characters to add in front of each member of the list
    :param empty_word: str - The word to use when the list is empty
    :return: str - The members of the list joined together intelligently
    """
    word_list = list(word_list)
    list_length = len(word_list)
    if list_length == 0:
        return empty_word
    elif list_length == 1:
        return '{0}{1}'.format(prefix, word_list[0])
    elif list_length == 2:
        return '{0}{1} {2} {0}{3}'.format(prefix, word_list[0], join_word, word_list[1])
    else:
        list_string = ''
        for item in word_list[:-1]:
            list_string += prefix + str(item) + ', '
        list_string += join_word + ' ' + prefix + word_list[-1]
        return list_string