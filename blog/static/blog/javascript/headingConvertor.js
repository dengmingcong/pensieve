"use strict";

class HeadingToTreeConverter {
  constructor(root) {
    this.root = root;
    this.walker = document.createTreeWalker(this.root, NodeFilter.SHOW_ALL, null);
  }

  convertHeadingToTree() {

  }

  isHeadingElement(node) {
    let pattern = /h\d/;
    return node instanceof Node
      && node.nodeType === 1
      && pattern.test(node.tagName.toLowerCase());
  }

  getFirstHeadingElement() {
    for (let node = this.walker.firstChild(); node !== null; node = this.walker.nextSibling()) {
      if (this.isHeadingElement(node)) {
        return node
      }
    }

    return null;
  }

  createFragmentContainer() {

  }
}

let article_content_section = document.querySelector("#main-content article section");
let converter = new HeadingToTreeConverter(article_content_section);

