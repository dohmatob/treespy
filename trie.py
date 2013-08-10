"""
:Author: d0hm4t06 3LV15 d0p91m4 <gmdopp@gmail.com>

"""

INFINITY = 1e100


def _full_label_to_str(full_label):
    """
    Default function.

    """

    return "".join([str(x) for x in full_label])


def list2html(l):
    """
    Function for converting a list into HTML (ul element).

    """

    return "<ul>%s</ul>" % "".join(["<li>%s</li>" % str(x) for x in l])


def _is_leaf(_):
    """
    Default function.

    """

    return False


def _is_bad_item(_):
    """
    Default function.

    """

    return False


def _handle_filename(x):
    import os

    for ext in ['.txt', '.md', '.rst']:
        if x.endswith(ext):
            return os.path.basename(x) + list2html(
                open(x).read().rstrip("\r\n").split("\n"))


class _Trie(object):
    def __init__(self, label=None, parent=None,
                 full_label_to_str=_full_label_to_str):
        """
        Parameters
        ----------
        label: some DataType
            the label of this node
        parent: `_Trie` object, optional (default None)
            the parent of this node
        full_label_to_str: function, optional
            a function which converts a list of labels to a single label

        """

        self.label = label
        self.full_label_to_str = full_label_to_str
        self.full_label = []
        self.set_parent(parent)
        self.children = []

        if not label is None:
            self.full_label.append(label)

    def is_root(self):
        """
        Checks whether self is root node.

        """

        return self.parent is None

    def set_parent(self, parent):
        """
        Sets the parent of this node, chaining the links as necessary

        Parameters
        ----------
        parent: `_Trie` object
            the would be parent of this node

        Returns
        -------
        self: `_Trie` object
            this node

        """

        self.parent = parent

        if not parent is None:
            parent.add_child(self)

        return self

    def is_leaf(self):
        """
        Checks whether self is leaf node.

        """

        return not self.children

    def add_child(self, child):
        """
        Adds a child to self.

        Parameters
        ----------
        child: Trie object
            child to be added to self

        Returns
        -------
        self: Trie instance
            self, after adding the child

        """

        child.full_label = list(self.full_label)
        self.children.append(child)
        child.parent = self

    def _full_label_as_str(self):
        """
        Converts the list self.full_label, into a string

        """

        return self.full_label_to_str(self.full_label)

    def display(self, padding=''):
        """
        Displays self, in a way similarly to the unix `tree` command.

        Parameters
        ----------
        padding: string, optional (default " ")
            controls indentation

        """

        if self.is_root():
            print " "
        else:
            print padding[:-1] + "+-" + self._full_label_as_str()

        padding += ' '

        count = 0
        for child in self.children:
            count += 1
            print padding + "|"
            if not child.is_leaf():
                if count == len(self.children):
                    child.display(padding=padding + ' ')
                else:
                    child.display(padding=padding + '|')
            else:
                print padding + '+-' + child._full_label_as_str() + "$"

    def as_html(self):
        """
        Converts self into an html string.

        Returns
        -------
        html: string
            HTML representation of self

        """

        html = "%s<ul>%s</ul>\r" % (self.label,
                                  "".join(["<li>%s</li>\r" % child.as_html()
                                           for child in self.children]))

        # handle tabs
        html = html.replace(" ", "&nbsp;")

        return html


def make_bt(depth, label=None, parent=None):
    """
    Creates a Binary Tree (BT).

    Parameters
    ----------
    depth: int
        depth of the binary tree
    label: int, optional (default 0)
        label of root node of the binary tree
    parent: Trie object, optional (default None)
        parent node of the binary tree

    """

    node = _Trie(label=label, parent=parent)

    if depth == 0:
        return node
    else:
        for label in xrange(2):
            make_bt(depth - 1, label=label, parent=node)

    return node


def as_trie(data, get_head, expand, is_leaf=_is_leaf, is_bad_item=_is_bad_item,
            depth=None, parent=None, full_label_to_str=_full_label_to_str):
    """
    Generates a trie representation of given data.

    Parameters
    ----------
    data: some DataType object
        the data to be trie-represented
    get_head: function
        a function on `DataType` which returns the head of the data. Thus
        the function must be useable as follows: head = get_head(data)
    expand: function
        a function on `DataType`which returns a generator or list_like of
        sub-data. Thus the function must be useable as follows: for
        sub_data in expand(data): do_something(sub_data)
    is_leaf: function, optional
        a function on `DataType` which returns True if the data if leaf,
        and False otherwise.
    is_bad_item: function, optional
        a function which, for each item returned by `expand`, whether the
        item if 'good' (i.e expandable) or not
    parent: `DataType` object, optional (default None)
        the parent of the data
    full_label_to_str: function
        a function which can join a list of `DataType` heads into a single
        head. For example if `DataType` represents paths on a linux system
        the this function would be similar to the os.path.join(function),
        i.e def full_label_to_str([a, b, ...]): return os.path.join(a, b, ...)

    Returns
    -------
    trie: `_Trie` object
        the trie representation of the data

    """

    # sanitize depth
    depth = INFINITY if depth is None else depth

    # pack head of data into _Trie node
    node = _Trie(label=get_head(data, parent), parent=parent,
                 full_label_to_str=full_label_to_str)

    if is_leaf(data) or depth == 0:
        # this is a leaf; end of expansion
        return node
    else:
        # expand each item which is not bad
        for x in expand(data):
            if not is_bad_item(x):
                try:  # exceptions might occur; consider them as dead-ends
                    if get_head(x) == -1:
                        continue

                    as_trie(x, get_head, expand,
                            is_leaf, is_bad_item=is_bad_item, depth=depth - 1,
                            parent=node, full_label_to_str=full_label_to_str)
                except:
                    continue

    # return _Trie node
    return node


def linux_tree(directory, depth=None,
               ignore_if_endswith=[".pyc", "~", "#"],
               ignore_if_startswith=['#'],
               handle_filename=_handle_filename,
               display=True):
    """
    A personal implementation of the famous linux tree command.

    Parameters
    ----------
    directory: string
        existing directory full path; directory to be expanded
    depth: int, optional (default None)
        max depth for expansion
    ignore_if_endswith: list of strings, optional (default [".pyc", "~", "#"])
        file extensions to ignore during expansion
    ignore_if_startswith: list of strings, optional (default ["#"])
        file prefices to ignore during expansion
    cat_if_endswith: list of strings, optional (default [])
        list of file extensions whose contents will be returned for their
        head (during calls to get_head(...))
    display: bool, optional (default True)
        display final trie structure

    Returns
    -------
    tree: `_Trie` object
        trie representation of the directory

    """

    import os

    def is_leaf(x):
        return os.path.isfile(x)

    def is_bad_item(x):
        for ext in ignore_if_endswith:
            if x.endswith(ext):
                return True

        for ext in ignore_if_startswith:
            if x.startswith(ext):
                return True

        return False

    def get_head(x, parent=None):
        z = x if parent is None else os.path.basename(x)

        if is_leaf(x):
            y = handle_filename(x)

            return y if not y is None else z
        else:
            return z

    def expand(x):
        return [os.path.join(x, y) for y in os.listdir(x)]

    def full_label_to_str(full_label):
        return os.path.join(*tuple(full_label))

    # get trie reprensetation
    trie = as_trie(directory, get_head, expand, is_leaf=is_leaf,
                   is_bad_item=is_bad_item, depth=depth,
                   full_label_to_str=full_label_to_str)

    # display trie
    if display:
        trie.display()

    return trie