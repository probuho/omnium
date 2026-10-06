"""Constantes de CSS para tema Monokai."""

MONOKAI_CSS = """
Screen {
    background: #272822;
    color: #f8f8f2;
}

.ascii-logo {
    text-align: center;
    color: #ae81ff;
    padding: 1 0;
    height: auto;
    overflow: hidden;
}

.divider {
    color: #75715e;
    text-align: center;
    margin: 0 0 1 0;
}

.main-container {
    width: 100%;
    height: 100%;
    padding: 0 2;
}

.url-label {
    color: #f8f8f2;
    margin-top: 1;
    margin-bottom: 0;
}

.input-group {
    margin: 0 0 1 0;
}

Input {
    background: #3e3d32;
    border: solid #75715e;
    color: #f8f8f2;
    padding: 0 1;
}

Input:focus {
    border: solid #ae81ff;
}

.validation {
    height: 1;
    margin: 0 0 1 0;
}

.sites-hint {
    height: 2;
    margin: 0 0 1 0;
    text-align: center;
    text-wrap: wrap;
}

.tab-group {
    margin: 1 0;
    height: 3;
}

.tab-group Button {
    margin-right: 1;
    min-width: 16;
}

.option-group {
    margin: 1 0;
}

.option-group.hidden {
    display: none;
}

.option-label {
    color: #ae81ff;
    margin: 1 0 0 0;
}

OptionList {
    background: #3e3d32;
    border: solid #75715e;
    color: #f8f8f2;
    margin: 0 0 1 0;
}

OptionList:focus {
    border: solid #ae81ff;
}

OptionList > .option-list--option-highlighted {
    background: #ae81ff;
    color: #272822;
}

.privacy-notice {
    margin-top: 2;
    padding: 1;
    background: #1e1f1c;
    border: solid #75715e;
    text-align: center;
    text-wrap: wrap;
}

.nav-hint {
    margin-top: 1;
    padding: 1;
    background: #1e1f1c;
    border: solid #75715e;
    text-align: center;
    color: #75715e;
}

.button-group {
    margin: 1 0;
    width: 100%;
    height: auto;
}

.button-group Button {
    margin-right: 1;
    background: #3e3d32;
    border: solid #75715e;
    color: #f8f8f2;
}

.button-group Button:hover {
    background: #4e4d3e;
    border: solid #ae81ff;
}

.button-group Button:focus {
    background: #4e4d3e;
    border: solid #ae81ff;
}

.button-group Button.focused {
    background: #4e4d3e;
    border: solid #ae81ff;
}

.button-group Button.-primary {
    background: #ae81ff;
    border: solid #ae81ff;
    color: #272822;
}

.button-group Button.-primary:hover {
    background: #cc99ff;
    border: solid #cc99ff;
}

.status {
    margin: 1 0;
    height: 1;
}

#progress {
    margin: 1 0;
    background: #3e3d32;
    color: #ae81ff;
}

.log {
    height: 12;
    background: #1e1f1c;
    border: solid #75715e;
    color: #f8f8f2;
    margin-top: 1;
    padding: 1;
}

.title {
    text-align: center;
    color: #ae81ff;
    padding: 1;
    margin-bottom: 1;
}

.settings-list {
    margin: 1 0;
}

.settings-list Label {
    margin-top: 1;
    color: #ae81ff;
}

.config-value {
    padding-left: 2;
    color: #75715e;
    overflow: hidden;
}

.sites-content {
    padding: 1 2;
    color: #f8f8f2;
    overflow-y: auto;
    height: 100%;
}

DataTable {
    height: 100%;
    background: #272822;
}

DataTable > .datatable--header {
    background: #3e3d32;
    color: #ae81ff;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #ae81ff;
    color: #272822;
}

.dialog {
    width: 60;
    height: auto;
    padding: 2;
    border: solid #ae81ff;
    background: #3e3d32;
}

.dialog-title {
    text-align: center;
    color: #ae81ff;
    margin-bottom: 1;
}

.dialog-message {
        text-align: center;
        color: #f8f8f2;
        margin-bottom: 2;
    }

.dialog-buttons {
    width: 100%;
}

.dialog-buttons Button {
    margin: 0 1;
}

Header {
    background: #272822;
    color: #75715e;
    border: solid #75715e;
    height: 2;
}

Footer {
    background: #272822;
    color: #75715e;
    border: solid #75715e;
}

Footer .key {
    color: #ae81ff;
}

Collapsible {
    border: solid #75715e;
    background: #272822;
}

Collapsible.-collapsed {
    border: solid #75715e;
}

CollapsibleTitle {
    color: #ae81ff;
    background: #3e3d32;
}
"""
