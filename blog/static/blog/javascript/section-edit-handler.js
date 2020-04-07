"use strict";

import { HeadingToTreeConverter } from "./heading-to-tree-converter.js";
import { SectionProcessor } from "./add-edit-button-for-headers.js";

/**
 * Returns the value of specified cookie.
 * @param name
 * @returns {null}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

/**
 * Handles when 'edit' button besides each section was clicked.
 * @param event
 */
const editClicked = function handlerWhenEditButtonClicked(event) {
  if (event.target.text === 'edit' && event.target.parentNode.className === 'edit-section') {
    event.preventDefault();
    let sectionContainer = event.target.parentNode.parentNode.parentNode;
    getSectionText(event.target.href, replaceElement, sectionContainer)
  }
};

/**
 * Initializes XHR and sends a GET request to retrieve inner text of specified section. When 'load' event triggers, callback another function.
 * @param url
 * @param callback
 * @param moreArgs
 */
const getSectionText = function getTextOfSpecifiedSectionAndPassResponseToCallback(url, callback, ...moreArgs) {
  let xhr = new XMLHttpRequest();
  xhr.callback = callback;
  xhr.url = url;
  xhr.moreArgs = moreArgs;
  xhr.addEventListener('load', xhrSuccess);
  xhr.open('get', url);
  xhr.send(null);
};

/**
 * Handles when 'load' event of XHR triggers.
 */
const xhrSuccess = function () {
  this.callback.apply(this, this.moreArgs);
};

/**
 * Replace an element with a form, which was filled with the response text of XHR.
 * @param oldElement
 */
const replaceElement = function replaceAnHTMLElementWithForm(oldElement) {
  // Create a new form element.
  let form = document.createElement('form');
  form.action = this.url;
  form.method = 'post';
  form.id = oldElement.getAttribute('data-seqnum');

  let textArea = document.createElement('textarea');
  textArea.value = JSON.parse(this.responseText)["section_text"];
  textArea.name = "section-text";

  let submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'Submit';

  form.appendChild(textArea);
  form.appendChild(submitButton);

  // Replace section with corresponding form element.
  oldElement.parentNode.replaceChild(form, oldElement);

  // Listen submit event on form element.
  form.addEventListener('submit', submitHandler, false);
};

/**
 * Handles when specified form was submitted.
 * @param event
 */
const submitHandler = function HandlerWhenSubmitButtonClicked(event) {
  event.preventDefault();
  submitForm(event.target, updateSection, event.target);
};

/**
 * Initializes an XHR to submit form data and callback other function when gotten response.
 * @param form Form to be submitted
 * @param callback
 * @param moreArgs
 */
const submitForm = function replaceFormWithNewSectionHTML(form, callback, ...moreArgs) {
  let csrftoken = getCookie('csrftoken');
  let xhr = new XMLHttpRequest();
  xhr.callback = callback;
  xhr.form = form;
  xhr.moreArgs = moreArgs;

  xhr.addEventListener('load', xhrSuccess);
  xhr.open("post", form.action);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.send(new FormData(form));
};

/**
 * Updating an section via replacing the form
 * @param form
 */
const updateSection = function updateSectionWithNewHTML(form) {
  let div = document.createElement('div');
  div.innerHTML = JSON.parse(this.responseText)["section_html"];

  let converter = new HeadingToTreeConverter(div);
  let headingIndexList = form.id.split(".").map(item => parseInt(item));
  let lastItem = headingIndexList.slice(-1)[0];

  // Minus 1 if last item is greater than 0.
  headingIndexList[headingIndexList.length -1] = lastItem > 0 ? lastItem - 1 : lastItem;
  converter.headingIndexList = headingIndexList;
  converter.convertHeadingToTree();

  // Add edit button.
  let sp = new SectionProcessor(converter.root, 3);
  sp.addEditButton();

  form.parentNode.replaceChild(div.firstChild, form);
};

let article_content = document.getElementById('article-content');
article_content.addEventListener('click', editClicked, false);
