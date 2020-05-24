"use strict";

const activeMarker = "selected";
const hiddenMarker = "hidden";
const postUrl = "/blog/preview-markdown";

let fileHeader = document.querySelector(".file-header");
let editTab = fileHeader.querySelector("[data-tab='show-code']");
let previewTab = fileHeader.querySelector("[data-tab='preview']");
let editPanel = document.querySelector(".commit-create");
let loadingPanel = document.querySelector(".loading-preview-msg");
let previewPanel = document.querySelector(".commit-preview");

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

const dispatchTabs = function dispatchToCodeOrPreview(event) {
  if (event.target === editTab) {
    codeTabClicked();
  } else if (event.target === previewTab) {
    previewTabClicked();
  }
}

const codeTabClicked = function handlerWhenCodeTabWasClicked() {
  if (!editTab.classList.contains(activeMarker)) {

    // Highlight edit tab.
    editTab.classList.add(activeMarker);

    // Un-highlight preview tab.
    previewTab.classList.remove(activeMarker);

    // Display editor panel.
    editPanel.classList.remove(hiddenMarker);

    // Hide preview panel.
    previewPanel.classList.add(hiddenMarker);
  }
}

const previewTabClicked = function handlerWhenPreviewTabWasClicked() {
  if (!previewPanel.classList.contains(activeMarker)) {

    // Highlight preview tab.
    previewTab.classList.add(activeMarker);

    // Un-highlight edit tab.
    editTab.classList.remove(activeMarker);

    // Hide editor panel.
    editPanel.classList.add(hiddenMarker);

    // Hide preview panel.
    previewPanel.classList.add(hiddenMarker);

    // Display loading panel.
    loadingPanel.classList.remove(hiddenMarker);

    let xhr = new XMLHttpRequest();
    let data = new FormData();
    let csrftoken = getCookie('csrftoken');
    data.append("origin-markdown", "### This is test text.")
    xhr.addEventListener('load', displayPreview);
    xhr.open("post", postUrl);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.send(data);
  }
}

const displayPreview = function displayPreviewWhenMarkdownTransformed(event) {
  loadingPanel.classList.add(hiddenMarker);
  previewPanel.innerHTML = JSON.parse(event.target.responseText)["html"];
  previewPanel.classList.remove(hiddenMarker);
}

fileHeader.addEventListener("click", dispatchTabs, false);
