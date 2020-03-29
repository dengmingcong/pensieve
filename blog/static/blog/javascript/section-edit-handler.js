"use strict";

const editClicked = function handlerWhenEditButtonClicked(event) {
  if (event.target.text === 'edit' && event.target.parentNode.className === 'edit-section') {
    event.preventDefault();
    let sectionContainer = event.target.parentNode.parentNode.parentNode;
    getSectionText(event.target.href, replaceElement, sectionContainer)
  }
};

const getSectionText = function getTextOfSpecifiedSectionAndPassResponseToCallback(url, callback, ...moreArgs) {
  let xhr = new XMLHttpRequest();
  xhr.callback = callback;
  xhr.url = url;
  xhr.moreArgs = moreArgs;
  xhr.addEventListener('load', xhrSuccess);
  xhr.open('get', url);
  xhr.send(null);
};

const xhrSuccess = function () {
  this.callback.apply(this, this.moreArgs);
};

const replaceElement = function replaceAnHTMLElementWithForm(oldElement) {
  let form = document.createElement('form');
  form.action = this.url;
  form.method = 'post';

  let textArea = document.createElement('textarea');
  textArea.value = JSON.parse(this.responseText)["content_xml"];

  let submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'Submit';

  form.appendChild(textArea);
  form.appendChild(submitButton);

  oldElement.parentNode.replaceChild(form, oldElement);
};

let article_content = document.getElementById('article-content');
article_content.addEventListener('click', editClicked, false);
