"""
:Author: d0hm4t06 3LV15 d0p91m4 <gmdopp@gmail.com>

"""

import os
import shutil
import glob

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
    """
    Default function.

    """

    for ext in ['.txt', '.md', '.rst']:
        if x.endswith(ext):
            return os.path.basename(x) + list2html(
                open(x).read().rstrip("\r\n").split("\n"))


def copy_web_conf_files(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for icon in glob.glob("icons/*.gif"):
        shutil.copy(icon, output_dir)

    for js in glob.glob("js/*.js"):
        shutil.copy(js, output_dir)


class _Tree(object):
    def __init__(self, label=None, parent=None,
                 full_label_to_str=_full_label_to_str):
        """
        Parameters
        ----------
        label: some DataType element, optional (default None)
            the label of this node
        parent: `_Tree` object, optional (default None)
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
        parent: `_Tree` object
            the would be parent of this node

        Returns
        -------
        self: `_Tree` object
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
        child: Tree object
            child to be added to self

        Returns
        -------
        self: Tree instance
            self, after adding the child

        """

        child.full_label = list(self.full_label)
        self.children.append(child)
        child.parent = self

    def _full_label_to_str(self):
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
            print padding[:-1] + "+-" + self._full_label_to_str()

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
                print padding + '+-' + child._full_label_to_str() + "$"

    def as_html(self, report_filename=None, full_label=False,
                title="Hierarchical report"):
        """
        Converts self into an html string.

        Returns
        -------
        html: string
            HTML representation of self

        """

        html = "%s<ul>%s</ul>\r\n" % (
            self.label if not full_label else self._full_label_to_str(),
            "".join(["<li>%s</li>\r\n" % child.as_html(full_label=full_label)
                     for child in self.children]))

        # handle tabs
        html = html.replace(" ", "&nbsp;")

        if not report_filename is None:
            report_filename = os.path.abspath(report_filename)

            if os.path.isfile(report_filename):
                os.remove(report_filename)

            copy_web_conf_files(os.path.dirname(report_filename))

            # grab report template
            report = open("hierarchical_report_template.tmpl.html").read()

            # generate report from template
            report = report.replace("{{i_am_the_body}}", html)
            report = report.replace("{{i_am_the_title}}", title)

            # write report unto disk
            open(report_filename, 'a').write(report)

            print report
            print "\r\nHTML report written to %s\r\n" % report_filename

        return html

    def as_dict(self):
        """
        Converts tree into dict.

        Returns
        -------
        name: string
            name of the dict
        d: dict
            the dict representation of this tree

        """

        return self.label, dict((child.label, child.as_dict()[1])
                                for child in self.children)


def make_nary_tree(depth, n, label=None, parent=None, alphabet=None):
    """
    Creates an n-ary tree of given depth.

    Parameters
    ----------
    depth: int
        depth of the binary tree
    n: int
        arity of the tree
    label: int, optional (default None)
        label of root node of the binary tree
    parent: Tree object, optional (default None)
        parent node of the binary tree
    alphabet: list of length n, optional (default)
        alphabet of symbols

    """

    label = alphabet[label] if (not None in [alphabet, label]
                                ) and isinstance(
        label, int) and 0 <= label < n else label

    node = _Tree(label=label, parent=parent)

    if depth == 0:
        return node
    else:
        for label in xrange(n):
            make_nary_tree(depth - 1, n, label=label, parent=node,
                           alphabet=alphabet)

    return node


def make_bt(depth):
    """
    Creates a binary tree of given depth.

    """

    return make_nary_tree(depth, 2)


def as_tree(data, get_head, expand, is_leaf=_is_leaf, is_bad_item=_is_bad_item,
            depth=None, parent=None, full_label_to_str=_full_label_to_str):
    """
    Generates a tree representation of given data.

    Parameters
    ----------
    data: some DataType object
        the data to be tree-represented
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
    tree: `_Tree` object
        the tree representation of the data

    """

    # sanitize depth
    depth = INFINITY if depth is None else depth

    # pack head of data into _Tree node
    node = _Tree(label=get_head(data, parent), parent=parent,
                 full_label_to_str=full_label_to_str)

    if is_leaf(data) or depth == 0:
        # this is a leaf; end of expansion
        return node
    else:
        # expand each item which is not bad
        for x in expand(data):
            print x,
            if not is_bad_item(x):
                if get_head(x) == -1:
                    continue

                as_tree(x, get_head, expand,
                        is_leaf, is_bad_item=is_bad_item, depth=depth - 1,
                        parent=node, full_label_to_str=full_label_to_str)
        print

    # return _Tree node
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
        display final tree structure

    Returns
    -------
    tree: `_Tree` object
        tree representation of the directory

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

    # get tree reprensetation
    tree = as_tree(directory, get_head, expand, is_leaf=is_leaf,
                   is_bad_item=is_bad_item, depth=depth,
                   full_label_to_str=full_label_to_str)

    # display tree
    if display:
        tree.display()

    return tree


def dict2tree(d, name="", parent=None):
    """
    Converts a dict into _Tree object.

    Parameters
    ----------
    d: dict
        dict object to be converted intto _Tree object
    name: string, optional (default "")
        the name of the dict
    parent: _Tree object, optional (default None)
        parent node of the node being generated

    Returns
    -------
    node: _Tree object
        tree representation of the input dict

    """

    node = _Tree(label=name, parent=parent)

    if isinstance(d, dict):
        for k, v in d.iteritems():
            if isinstance(v, dict):
                dict2tree(v, name=k, parent=node)
            else:
                _Tree(label='%s: %s' % (k, v), parent=node)

    return node


if __name__ == "__main__":
    output_dir = "/tmp/pytrees_demo"

    # current directory listing
    print "\r\nBuilding current directory listing..."
    linux_tree(os.path.abspath("."), display=False).as_html(
        report_filename=os.path.join(output_dir, 'linux_tree.html'),
        title="Current directory listing"
        )

    # binary tree
    print "\r\nBuilding binary tree..."
    make_bt(10).as_html(report_filename=os.path.join(output_dir, "bt.html"),
                             title="Binary Tree",
                             full_label=True)

    # english 3-grams
    print "\r\nBuilding all english 2-grams..."
    make_nary_tree(2, 26, alphabet=[chr(x + ord('a')) for x in xrange(26)]
                   ).as_html(report_filename=os.path.join(output_dir,
                                                          "2_grams.html"),
                             title="English Language 2-grams",
                             full_label=True)

    # locals
    print "\r\nBuilding locals()..."
    dict2tree(locals(), name="locals").as_html(
        report_filename=os.path.join(output_dir, "locals.html"),
        title="Python locals"
        )
