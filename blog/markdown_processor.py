import logging
import re
import xml.etree.ElementTree as ET

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


class MarkdownProcessor(object):
    """
    A simple markdown processor.

    differences from lib Python-Markdown:
        1. Only hash header will be handled specially.
        2. Non-header lines would be placed in <p>.
        3. Entire line would be set as value of element's attribute 'text', including empty lines.
    """
    def __init__(self, doc):
        self.doc = doc
        self.root = ET.Element('root')
        self.tree = ET.ElementTree(self.root)
        self.parent_map = {}
        self.id_list = []

    def to_xml(self):
        """
        Turns markdown document to xml.

        For instance, string "## h2" would output:
            <root>
                <h id="0.1" level="2">## h2</h>
            </root>.
        """
        lines = self.doc.split('\r\n')
        sub_tree_root = self.root
        parent = self.root
        # with open(self.doc, 'r') as f:
        #    lines = f.read().splitlines()

        for line in lines:
            logging.info("line: {}".format(line))
            logging.info("sub tree root now: {}".format(sub_tree_root.text))
            if self.is_hash_header(line):
                header_level = self.get_hash_header_level(line)
                h = ET.Element('h', {'level': str(header_level)})
                h.text = line
                self.set_header_id(h)
                parent = self.find_parent(self.root, sub_tree_root, h)
                logging.info("parent element returned: {}".format(parent.text))
                parent.append(h)
                self.parent_map[h] = parent
                sub_tree_root = h
            else:
                p = ET.Element('p')
                p.text = line
                sub_tree_root.append(p)
                self.parent_map[p] = parent

    def find_parent(self, root, sub_tree_root, h):
        """
        Find an element as parent of header.

        :param root: root element of the entire tree
        :param sub_tree_root: root element of sub-tree
        :param h: a header element
        :return: an element
        """
        parent = None
        if sub_tree_root == root:
            parent = root
        else:
            sub_tree_level = int(sub_tree_root.get("level"))
            header_level = int(h.get("level"))
            result = header_level - sub_tree_level
            if result > 0:
                parent = sub_tree_root
            elif result == 0:
                parent = self.parent_map[sub_tree_root]
            else:
                parent = self.find_parent(root, self.parent_map[sub_tree_root], h)

        return parent

    def set_header_id(self, h):
        """
        Add attribute 'id', e.g. 'id'='0.0.1' for first level 3 header.

        :param h: header element
        :return: nothing
        """
        header_level = int(h.get("level"))
        id_list_length = len(self.id_list)
        if header_level > id_list_length:
            self.id_list.extend([0] * (header_level - id_list_length))
        else:
            self.id_list = self.id_list[:header_level]

        self.id_list[-1] += 1
        header_id = ".".join(map(str, self.id_list))
        logging.info("header id: {}".format(header_id))
        h.set('id', header_id)

    @staticmethod
    def is_hash_header(line):
        """
        Returns True if given line is hash header.

        :param line: a string representing one line in text file.
        :rtype: bool
        """
        pattern = re.compile(r'(?:^|\n)(?P<level>#{1,6})(?P<header>(?:\\.|[^\\])*?)#*(?:\n|$)')
        return bool(pattern.search(line))

    @staticmethod
    def get_hash_header_level(line):
        """
        Returns a digit representing level of the hash header. In particular, the count of '#'.

        :param line: one line of a text file
        :return: a digit
        """
        pattern = re.compile(r'(?:^|\n)(?P<level>#{1,6})(?P<header>(?:\\.|[^\\])*?)#*(?:\n|$)')
        matches = pattern.search(line)
        return len(matches.group('level'))


if __name__ == '__main__':
    # md = MarkdownProcessor('/tmp/test-python/a')
    md = MarkdownProcessor('## h2')
    md.to_xml()
    ET.dump(md.root)
