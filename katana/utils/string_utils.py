def split_str_at_last_index(str, split_at):
    """
    This function splits a string at the last index of the character in "split_at"
    Args:
        str: String to be split
        split_at: Character at which the string should be split

    Returns:

        output = remaining string after splitting

    """
    temp = str.split(split_at)

    output = ""
    for j in range(0, len(temp) - 1):
        output += temp[j]
        output += split_at

    output = output.strip(split_at)

    return output


def remove_trailing_characters_from_string(element, char_list):
    """
    This function removes trailing characters from a given string

    Args:
        element: String to be formatted
        char_list: List of characters to be removed from that string

    Returns:
        element: formatted string

    """
    for el in char_list:
        element = element.strip(el)

    return element


def remove_trailing_characters_from_list(element_list, char_list):
    """
    This function removes trailing characters from a all strings in a list
    Args:
        element_list: list of strings to be formatted
        char_list: List of characters to be removed from each string in the list

    Returns:
        element_list: list of formatted strings

    """
    for i in range(0, len(element_list)):
        for el in char_list:
            element_list[i] = element_list[i].strip(el)
    return element_list
