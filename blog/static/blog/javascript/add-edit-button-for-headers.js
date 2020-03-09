"use strict";

class SectionProcessor {
  constructor(root, topEditableHeaderLevel) {
    this.root = root;
    this.topEditableHeaderLevel = topEditableHeaderLevel;
    this.targetElementTag = 'section';
    this.headingLevelAttribute = 'data-heading-level';
    this.seqNumAttribute = 'data-seqnum';
  }

  /**
   * Add 'edit' button aside heading element's innerText.
   */
  addEditButton() {
    let filter = (node) => {
      return (node.tagName.toLowerCase() === this.targetElementTag &&
        node.hasAttribute(this.headingLevelAttribute) &&
        node.hasAttribute(this.seqNumAttribute) &&
        this.hasHigherLevel(node)) ?
        NodeFilter.FILTER_ACCEPT :
        NodeFilter.FILTER_SKIP;
    };

    let walker = document.createTreeWalker(this.root, NodeFilter.SHOW_ELEMENT, filter);
    let node = walker.nextNode();
    let edit_url = '';

    while (node !== null) {
      edit_url = location.pathname + node.getAttribute(this.seqNumAttribute) + "/edit";
      this.appendEditButton(node.firstChild, edit_url);
      node = walker.nextNode();
    }
  }

  /**
   * Returns true if the level of given node is higher than or equal to setting level.
   * @param node An HTMLElement which has specific attribute.
   * @returns {boolean}
   */
  hasHigherLevel(node) {
    let level = parseInt(/h(\d)/.exec(node.getAttribute(this.headingLevelAttribute))[1]);
    return level <= this.topEditableHeaderLevel;
  }

  /**
   * Append an anchor element to specific heading, two brackets and outer container would be added too.
   * @param h An instance of HTMLHeadingElement.
   * @param url
   */
  appendEditButton(h, url) {
    let editContainer = document.createElement('span');
    editContainer.classList.add("edit-section");

    let leftBracket = document.createElement('span');
    leftBracket.classList.add("edit-section-bracket");
    leftBracket.innerText = '[';

    let editButton = document.createElement('a');
    editButton.href = url;
    editButton.innerText = "edit";

    let rightBracket = document.createElement('span');
    rightBracket.classList.add("edit-section-bracket");
    rightBracket.innerText = ']';

    editContainer.appendChild(leftBracket);
    editContainer.appendChild(editButton);
    editContainer.appendChild(rightBracket);
    h.appendChild(editContainer);
  }
}



let root = document.querySelector("#article-content");
let sp = new SectionProcessor(root, 3);
sp.addEditButton();
