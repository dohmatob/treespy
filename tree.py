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


def copy_web_conf_files(output_dir):
    """
    Copy web config files to output_dir.

    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for icon in glob.glob("icons/*.gif"):
        shutil.copy(icon, output_dir)

    for js in glob.glob("js/*.js"):
        shutil.copy(js, output_dir)


class _Tree(object):
    """
    Tree data structure.

    A tree is an acylic digraph. There is a natural ordering on such a
    structure, namely:

        a < b iff 'a is the parent of b'

    All the children of a node must have distinct labels (similary to names
    amongst children in a family)

    """

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

        return self

    def _full_label_to_str(self, full_label=True):
        """
        Converts the list self.full_label, into a string

        """

        return str(self.label) if not full_label else self.full_label_to_str(
            self.full_label)

    def display(self, padding='', full_label=True, root_here=False):
        """
        Displays self, in a way similarly to the unix `tree` command.

        Parameters
        ----------
        padding: string, optional (default " ")
            controls indentation

        """

        if self.is_root() or root_here:
            print " %s" % str(self.label) if root_here else ""
        else:
            print padding[:-1] + "+-" + self._full_label_to_str(
                full_label=full_label)

        padding += ' '

        count = 0
        for child in self.children:
            count += 1
            print padding + "|"
            if not child.is_leaf():
                if count == len(self.children):
                    child.display(padding=padding + ' ', full_label=full_label)
                else:
                    child.display(padding=padding + '|', full_label=full_label)
            else:
                print padding + '+-' + child._full_label_to_str(
                    full_label=full_label) + "$"

    def is_ul(self):
        """
        Checks wether this node is a ul.

        """

        # XXX the check done below is only heuristic;
        # it's not ultimately reliable
        for ul_marker in ['<ul>', '</ul>']:
            if not ul_marker in str(self.label):
                return False
            for li_marker in ['<li>', '</li>']:
                if not li_marker in str(self.label):
                    return False

        return True

    def as_html(self, report_filename=None, full_label=False,
                title="Hierarchical report"):
        """
        Converts self into an html string.

        Returns
        -------
        html: string
            HTML representation of self

        """

        label = self.label if not full_label else self._full_label_to_str()

        open_ul, close_ul = ("", "")
        if not self.is_leaf():
            open_ul, close_ul = ("<ul>", "</ul>")

        html = "%s%s" % (label, open_ul)

        # all non-leaf children
        for child in self.children:
            if not child.is_leaf():
                html += "<li>%s</li>" % child.as_html(full_label=full_label)

        # all ul leaf children
        for child in self.children:
            if child.is_leaf() and child.is_ul():
                html += "<li>%s</li>" % child.as_html(full_label=full_label)

        # all leaf non-ul children
        for child in self.children:
            if child.is_leaf() and not child.is_ul():
                html += "<li>%s</li>" % child.as_html(full_label=full_label)

        html += close_ul

        # handle tabs
        html = html.replace(" ", "&nbsp;")

        if not report_filename is None:
            report_filename = os.path.abspath(report_filename)

            # remove old report
            if os.path.isfile(report_filename):
                os.remove(report_filename)

            # copy web config
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

    # def merge(self, other_tree, **root_kwargs):
    #     """
    #     Merges self with other_tree.

    #     Returns
    #     -------
    #     : _Trie object
    #         the trie resulting from merging self with other_tree

    #     Notes
    #     -----
    #     After merging, both self and other tree disown their previous,
    #     parents.

    #     """

    #     root = _Tree(**root_kwargs)

    #     for child in [self, other_tree]:
    #         if child.is_root():
    #             for grandchild in child.children:
    #                 root.add_child(grandchild)
    #         else:
    #             root.add_child(child)

    #     return root

    def get_descendant(self, path):
        return self if not path else self.children[path[0]].get_descendant(
            path[1:])

    def __iter__(self):
        """
        An iterator on the  nodes of tree rooted at self.

        """

        yield self
        for child in self.children:
            for grandchild in child.__iter__():
                yield grandchild

    def __str__(self):
        return self.as_dict().__str__()


def make_nary_tree(n, depth, label=None, parent=None, alphabet=None):
    """
    Creates an n-ary tree of given depth.

    Parameters
    ----------
    n: int
        arity of the tree
    depth: int
        depth of the binary tree
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
            make_nary_tree(n, depth - 1, label=label, parent=node,
                           alphabet=alphabet)

    return node


def make_bt(depth, **kwargs):
    """
    Creates a binary tree of given depth.

    """

    return make_nary_tree(2, depth, **kwargs)


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


def folder2tree(folder, current_depth=0, max_depth=None, parent=None,
                handle_filename=None):
    """
    Expands a folder into a tree (cf. linux tree command).

    Parameters
    ----------
    folder: string
        existing folder
    current_depth: int, optional (default 0)
        a pointer to the current level in the tree structure
    max_depth: int, optional (default None)
        maximum depth to which the folder will be expanded
    parent: _Trie object, optional (default None)
        parent of this node
    handle_filename: (char *)(*)(const char *), optional (default None)
        function on strings, returing a string. Given a filename, this
        function should generate a string (perhaps scraped from the file),
        which will be reported as part of the file info

    """

    def path_join(x):
        return os.path.join(*tuple(x))

    def get_head(x):
        head = os.path.abspath(x)
        if not parent is None:
            head = os.path.basename(head)

        if os.path.isfile(x):
            if handle_filename is None:
                file_data = ""
                if x.endswith('.txt'  # cat text files
                              ):
                    file_data = list2html(open(x).read().rstrip(
                            "\r\n").split("\n"))
            else:
                file_data = handle_filename(x)

            head = head + file_data

        return head

    max_depth = INFINITY if max_depth is None else max_depth

    node = _Tree(label=get_head(folder), parent=parent,
                 full_label_to_str=path_join)

    if current_depth < max_depth and os.path.isdir(folder):
        try:
            # list the folder (sorted)
            for item in sorted(os.listdir(folder)):
                item = os.path.join(folder, item)
                if not parent is None:
                    item = os.path.join(parent._full_label_to_str(), item)
                folder2tree(item, parent=node, current_depth=current_depth + 1,
                            max_depth=max_depth,
                            handle_filename=handle_filename)
        except OSError:
            pass

    return node


if __name__ == "__main__":
    output_dir = "/tmp/treespy_demo"

    # binary tree
    print "\r\nBuilding binary tree..."
    make_bt(10).as_html(report_filename=os.path.join(output_dir, "bt.html"),
                             title="Binary Tree",
                             full_label=True)

    # english 2-grams
    print "\r\nBuilding all english 2-grams..."
    make_nary_tree(26, 2, alphabet=[chr(x + ord('a')) for x in xrange(26)]
                   ).as_html(report_filename=os.path.join(output_dir,
                                                          "2_grams.html"),
                             title="English Language 2-grams",
                             full_label=True)

    # locals
    print "\r\nBuilding locals()..."
    env = dict(os.environ)
    dict2tree(locals(), name="locals").as_html(
        report_filename=os.path.join(output_dir, "locals.html"),
        title="Python locals"
        )

    # current directory listing
    print "\r\nBuilding current directory listing..."
    folder2tree(os.path.abspath(".")).as_html(
        report_filename=os.path.join(output_dir, 'linux_tree.html'),
        title="Current directory listing"
        )
