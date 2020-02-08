"use strict";

class HeadingToTreeConverter {
  constructor(root) {
    this.root = root;
    this.walker = document.createTreeWalker(this.root, NodeFilter.SHOW_ALL, null);
    this.containerElementTag = 'section';
    this.levelAttributeName = 'data-heading-level';
  }

  convertHeadingToTree() {
    let fragment = document.createDocumentFragment();
    let firstChild = this.walker.firstChild()
    let currentNode = firstChild.cloneNode(true);
    let currentContainerElement = fragment;
    let parentContainerElement = null;
    let currentHeadingLevel = '';
    let node = null;

    while (currentNode !== null) {
      if (this.isHeadingElement(currentNode)) {
        // tag name (lower case, e.g. 'h2') as heading level.
        currentHeadingLevel = currentNode.tagName.toLowerCase();
        parentContainerElement = this.locateParentContainerElement(fragment, currentContainerElement, currentNode);
        currentContainerElement = this.createAndAppendContainerElement(parentContainerElement, currentNode, this.containerElementTag, this.levelAttributeName, currentHeadingLevel);
      } else {
        currentContainerElement.appendChild(currentNode);
      }

      node = this.walker.nextSibling();
      currentNode = node.cloneNode(true);
    }

    this.root.appendChild(fragment);
  }

  /**
   * Locates container element whose heading level is less than given heading element.
   * @param root Root element of the element tree, document fragment usually.
   * @param currentContainerElement Root or some container element with attribute 'data-heading-level'.
   * @param headingElement Heading element compared.
   * @returns {null|*}
   */
  locateParentContainerElement(root, currentContainerElement, headingElement) {
    let parentContainerElement = null;
    let lastHeadingLevel = '';
    let currentHeadingLevel = '';
    let result = NaN;

    if (currentContainerElement === root) {
      parentContainerElement = root;
    } else {
      lastHeadingLevel = currentContainerElement.getAttribute(this.levelAttributeName);
      currentHeadingLevel = headingElement.tagName.toLowerCase();
      result = this.compareHeadingLevel(currentHeadingLevel, lastHeadingLevel);
      switch (result) {
        case 1:
          parentContainerElement = currentContainerElement;
          break;
        case 0:
          parentContainerElement = currentContainerElement.parentNode();
          break;
        case -1:
          parentContainerElement = this.locateParentContainerElement(root, currentContainerElement.parentNode, headingElement);
          break;
      }
    }

    return parentContainerElement;
  }

  /**
   * Creates an element as container of current node, the new container element will be appended properly as well.
   * @param parentNode The node which the new created container element will appended to.
   * @param currentNode The node which will be appended to new created container element.
   * @param attributeValue The value set to self-defined attribute.
   * @param tagName Tag name of container element.
   * @param attributeName The name of self-defined attribute.
   * @returns {HTMLElement}
   */
  createAndAppendContainerElement(parentNode, currentNode, tagName, attributeName, attributeValue) {
    let containerElement = document.createElement(tagName);

    // example of container element: <section data-heading-level='h2'></section>
    containerElement.setAttribute(attributeName, attributeValue);
    containerElement.appendChild(currentNode);
    parentNode.appendChild(containerElement);
    return containerElement;
  }

  /**
   * Returns true if given node is instance of HTMLHeadingElement.
   * @param node
   * @returns {*|boolean}
   */
  isHeadingElement(node) {
    return node instanceof HTMLHeadElement;
  }

  /**
   * Returns first HTML element matching '/h\d/'.
   * @deprecated
   * @returns {*|Node|null} Returns first heading element if exists.
   */
  getFirstHeadingElement() {
    for (let node = this.walker.firstChild(); node !== null; node = this.walker.nextSibling()) {
      if (this.isHeadingElement(node)) {
        return node
      }
    }

    return null;
  }

  /**
   * Returns 0 if equal, 1 if heading1 is greater than heading2, -1 if heading1 is less than heading2.
   * @param {string} heading1 Tag name of heading element.
   * @param {string} heading2 Tag name of another heading element.
   * @returns {number}
   */
  compareHeadingLevel(heading1, heading2) {
    let pattern = /h(\d)/;
    if (!pattern.test(heading1) || !pattern.test(heading2)) {
      throw "Both parameters should be tag name of heading element, as 'h1, h2, ...'"
    }

    let matches1 = pattern.exec(heading1);
    let matches2 = pattern.exec(heading2);
    let level1 = parseInt(matches1[1]);
    let level2 = parseInt(matches2[1]);

    if (level1 === level2) {
      return 0;
    } else if (level1 > level2) {
      return 1;
    } else {
      return -1;
    }
  }
}

let article_content_section = document.querySelector("#main-content article section");
let converter = new HeadingToTreeConverter(article_content_section);
converter.convertHeadingToTree();