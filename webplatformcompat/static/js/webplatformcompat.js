"use strict";
/*global window: false, document: false, WPC: false */

window.WPC = {
    parse_resources: function (obj) {
        /* Parse resources from a JSON API response */
        var key, value, rType, rItem, rArray, rIdx, rCnt, resources = {};

        for (key in obj) {
            if (obj.hasOwnProperty(key)) {
                value = obj[key];
                if (key === 'linked') {
                    /* linked is a dictionary of resource type strings
                     * ("browsers", "versions", etc.) to an array of
                     * resource representations.  Turn this into a
                     * dictionary of IDs to representations
                     */
                    for (rType in value) {
                        if (value.hasOwnProperty(rType)) {
                            resources[rType] = {};
                            rArray = value[rType];
                            rCnt = rArray.length;
                            for (rIdx = 0; rIdx < rCnt; rIdx += 1) {
                                rItem = rArray[rIdx];
                                resources[rType][rItem.id] = rItem;
                            }
                        }
                    }
                } else if (key === 'meta' || key === 'links') {
                    /* "meta" is meta data for the request, such as pagination
                     * "links" contains link patterns for related objects
                     * Copy to the resources
                     */
                    resources[key] = obj[key];
                } else {
                    /* Key is a resource type string ("browsers", etc.)
                     * and value is the main item.  Copy to the special
                     * "data" key, as well as the resource by type by ID lookup
                     */
                    value = obj[key];
                    if (!resources.hasOwnProperty(key)) {
                        resources[key] = {};
                    }
                    resources[key][value.id] = value;
                    resources.data = value;
                }
            }
        }
        return resources;
    },
    trans_span: function (trans, lang) {
        var span = document.createElement('span');
        span.innerHTML = this.trans_str(trans, lang);
        return span;
    },
    trans_str: function (trans, lang) {
        if (trans === null || trans === undefined) {
            return null;
        }
        if (typeof trans === 'string') {
            return "<code>" + trans + "</code>";
        }
        if (trans.hasOwnProperty(lang)) {
            return trans[lang];
        }
        if (trans.hasOwnProperty('en')) {
            return trans.en;
        }
        return '';
    },
    generate_specification_table: function (resources, lang) {
        var table, thead, tbody, tr, th, td, a, rCnt, rIdx, resourceId,
            section, spec, maturity, matClass, small, span, reference;
        if (resources.data.links.references) {
            // Create the table
            table = document.createElement('table');
            table.setAttribute('class', 'wpc-specifications-table table');

            // Create the table header
            thead = document.createElement('thead');
            tr = document.createElement('tr');
            th = document.createElement('th');
            th.innerHTML = "Specification";
            tr.appendChild(th);
            th = document.createElement('th');
            th.innerHTML = "Status";
            tr.appendChild(th);
            th = document.createElement('th');
            th.innerHTML = "Comment";
            tr.appendChild(th);
            thead.appendChild(tr);
            table.appendChild(thead);

            // Create the table body
            tbody = document.createElement('tbody');
            rCnt = resources.data.links.references.length;
            for (rIdx = 0; rIdx < rCnt; rIdx += 1) {
                resourceId = resources.data.links.references[rIdx];
                reference = resources.references[resourceId];
                section = resources.sections[reference.links.section];
                spec = resources.specifications[section.links.specification];
                maturity = resources.maturities[spec.links.maturity];
                matClass = "maturity-" + maturity.slug;
                tr = document.createElement('tr');

                td = document.createElement('td');
                a = document.createElement('a');
                a.setAttribute('href', this.trans_str(spec.uri, lang) + this.trans_str(section.subpath, lang));
                a.appendChild(this.trans_span(spec.name, lang));
                a.appendChild(document.createElement('br'));
                small = document.createElement('small');
                small.appendChild(this.trans_span(section.number, lang));
                small.appendChild(document.createTextNode(' '));
                small.appendChild(this.trans_span(section.name, lang));
                a.appendChild(small);
                td.appendChild(a);
                tr.appendChild(td);

                td = document.createElement('td');
                span = this.trans_span(maturity.name, lang);
                span.setAttribute('class', matClass);
                td.appendChild(span);
                tr.appendChild(td);

                td = document.createElement('td');
                if (section.note) {
                    td.appendChild(this.trans_span(section.note, lang));
                }
                tr.appendChild(td);

                tbody.appendChild(tr);
            }
            table.appendChild(tbody);

            return table;
        }
        return null;
    },
    generate_browser_tables: function (resources, lang) {
        var a, backlink, browser, browserCnt, browserId, browserIdx, note,
            noteArray, noteCnt, noteDiv, noteId, noteIdx, noteNum, idPrefix,
            panel, support, supportId, supportMap, tab, tabCnt, tabContent,
            tabContentItem, tabId, tabIdx, tabList, tabListItem, table, tabs,
            tbody, th, thead, tr;
        if (resources.meta.compat_table.tabs) {
            idPrefix = 'wpc-compat-' + resources.data.id;
            tabs = resources.meta.compat_table.tabs;
            tabCnt = tabs.length;

            // Add bootstrap tab control for browser types (Desktop, etc.)
            panel = document.createElement('div');
            panel.setAttribute('role', 'tabpanel');
            tabList = document.createElement('ul');
            tabList.setAttribute('class', 'nav nav-tabs');
            tabList.setAttribute('role', 'tablist');
            tabContent = document.createElement('div');
            tabContent.setAttribute('class', 'tab-content');
            for (tabIdx = 0; tabIdx < tabCnt; tabIdx += 1) {
                tab = tabs[tabIdx];
                tabId = idPrefix + '_' + tabIdx;

                tabListItem = document.createElement('li');
                tabListItem.setAttribute('role', 'presentation');
                if (tabIdx === 0) {
                    tabListItem.setAttribute('class', 'active');
                }
                a = document.createElement('a');
                a.setAttribute('href', "#" + tabId);
                a.setAttribute('aria-controls', tabId);
                a.setAttribute('role', 'tab');
                a.setAttribute('data-toggle', 'tab');
                a.appendChild(this.trans_span(tab.name, lang));
                tabListItem.appendChild(a);
                tabList.appendChild(tabListItem);

                tabContentItem = document.createElement('div');
                tabContentItem.setAttribute('role', 'tabpanel');
                tabContentItem.setAttribute('id', tabId);
                if (tabIdx === 0) {
                    tabContentItem.setAttribute('class', 'tab-pane active');
                } else {
                    tabContentItem.setAttribute('class', 'tab-pane');
                }

                // Add the compat table for browser type
                table = document.createElement('table');
                table.setAttribute('class', 'table table-striped compat-table');

                thead = document.createElement('thead');

                tr = document.createElement('tr');
                th = document.createElement('th');
                th.appendChild(document.createTextNode('Feature'));
                tr.appendChild(th);

                browserCnt = tab.browsers.length;
                for (browserIdx = 0; browserIdx < browserCnt; browserIdx += 1) {
                    browserId = tab.browsers[browserIdx];
                    browser = resources.browsers[browserId];
                    th = document.createElement('th');
                    th.appendChild(this.trans_span(browser.name, lang));
                    tr.appendChild(th);
                }
                thead.appendChild(tr);

                // Add the compat table body (rows of sub-features)
                tbody = document.createElement('tbody');
                WPC.generate_browser_rows(resources.data.id, resources, lang, tab, tbody);
                table.appendChild(thead);
                table.appendChild(tbody);
                tabContentItem.appendChild(table);
                tabContent.appendChild(tabContentItem);
            }

            // Add notes
            if (resources.meta.compat_table.notes) {
                supportMap = resources.meta.compat_table.notes;
                noteArray = [];
                for (supportId in supportMap) {
                    if (supportMap.hasOwnProperty(supportId)) {
                        support = resources.supports[supportId];
                        noteNum = supportMap[supportId];
                        note = document.createElement('p');
                        noteId = 'wpc-compat-' + resources.data.id + '-note-' + noteNum;
                        note.setAttribute('id', noteId);
                        backlink = document.createElement('a');
                        backlink.setAttribute('href', '#' + noteId + '-back');
                        backlink.appendChild(document.createTextNode('[' + noteNum + ']'));
                        note.appendChild(backlink);
                        note.appendChild(document.createTextNode(' '));
                        note.appendChild(this.trans_span(support.note, lang));
                        noteArray[noteNum] = note;
                    }
                }
                noteDiv = document.createElement('div');
                noteDiv.setAttribute('id', 'wpc-compat-' + resources.data.id + '-notes');
                noteCnt = noteArray.length;
                for (noteIdx = 1; noteIdx < noteCnt; noteIdx += 1) {
                    noteDiv.appendChild(noteArray[noteIdx]);
                }
            } else {
                noteDiv = null;
            }

            panel.appendChild(tabList);
            panel.appendChild(tabContent);
            if (noteDiv) {
                panel.appendChild(noteDiv);
            }
            return panel;
        }
        return null;
    },
    generate_browser_rows: function (featureId, resources, lang, tab, tbody) {
        // Add row for feature and children when they have support
        var browserCnt, browserId, browserIdx, browserMap, childCnt, childId,
            childIdx, feature, featureName, hasSupports, note, noteId, noteNum,
            noteSup, nosupport, prefix, releaseUri, span1, span2, support,
            supportCnt, supportId, supportIdx, supportMap, supports, td, tr,
            unknown, version, versionId, versionLink;
        if (featureId === resources.data.id) {
            feature = resources.data;
            featureName = this.trans_span(this.strings['Basic support'], lang);
        } else {
            feature = resources.features[featureId];
            featureName = this.trans_span(feature.name, lang);
        }
        supportMap = resources.meta.compat_table.supports;
        if (supportMap.hasOwnProperty(featureId)) {
            browserMap = supportMap[featureId];
            hasSupports = (feature.links.supports && feature.links.supports.length > 0);
        } else {
            hasSupports = false;
        }
        if (hasSupports) {
            tr = document.createElement('tr');
            td = document.createElement('td');
            td.appendChild(featureName);
            if (feature.experimental) {
                span1 = document.createElement('span');
                span1.setAttribute('class', 'glyphicon glyphicon-fire');
                span1.setAttribute('style', 'color: #09d;');
                span1.setAttribute('aria-hidden', 'true');
                span1.setAttribute('data-toggle', 'tooltip');
                span1.setAttribute('data-placement', 'top');
                span1.setAttribute('title', 'This is an experimental API that should not be used in production code.');
                span2 = document.createElement('span');
                span2.setAttribute('class', 'sr-only');
                span2.appendChild(document.createTextNode('This is an experimental API that should not be used in production code.'));
                td.appendChild(span1);
                td.appendChild(span2);
            }
            if (!feature.standardized) {
                span1 = document.createElement('span');
                span1.setAttribute('class', 'glyphicon glyphicon-warning-sign');
                span1.setAttribute('style', 'color: #db0;');
                span1.setAttribute('aria-hidden', 'true');
                span1.setAttribute('data-toggle', 'tooltip');
                span1.setAttribute('data-placement', 'top');
                span1.setAttribute('title', 'This API has not been standardized.');
                span2 = document.createElement('span');
                span2.setAttribute('class', 'sr-only');
                span2.appendChild(document.createTextNode('This API has not been standardized.'));
                td.appendChild(span1);
                td.appendChild(span2);
            }
            if (feature.obsolete) {
                span1 = document.createElement('span');
                span1.setAttribute('class', 'glyphicon glyphicon-thumbs-down');
                span1.setAttribute('style', 'color: #000;');
                span1.setAttribute('aria-hidden', 'true');
                span1.setAttribute('data-toggle', 'tooltip');
                span1.setAttribute('data-placement', 'top');
                span1.setAttribute('title', 'This deprecated API should no longer be used, but will probably still work.');
                span2 = document.createElement('span');
                span2.setAttribute('class', 'sr-only');
                span2.appendChild(document.createTextNode('This deprecated API should no longer be used, but will probably still work.'));
                td.appendChild(span1);
                td.appendChild(span2);
            }
            tr.appendChild(td);

            browserCnt = tab.browsers.length;
            for (browserIdx = 0; browserIdx < browserCnt; browserIdx += 1) {
                // Add each version / support for sub-feature / browser
                td = document.createElement('td');
                browserId = tab.browsers[browserIdx];
                supports = browserMap[browserId];
                supportCnt = supports && supports.length;
                if (supportCnt) {
                    for (supportIdx = 0; supportIdx < supportCnt; supportIdx += 1) {
                        supportId = supports[supportIdx];
                        support = resources.supports[supportId];
                        versionId = support.links.version;
                        version = resources.versions[versionId];

                        // Version with support text
                        if (supportIdx !== 0) {
                            td.appendChild(document.createElement('br'));
                        }
                        if (version.version !== 'current') {
                            releaseUri = this.trans_str(version.release_notes_uri, lang);
                            if (releaseUri) {
                                versionLink = document.createElement('a');
                                versionLink.setAttribute('href', releaseUri);
                                versionLink.setAttribute('title', 'Release Notes');
                                versionLink.appendChild(document.createTextNode(version.version));
                                td.appendChild(versionLink);
                            } else {
                                td.appendChild(document.createTextNode(version.version));
                            }
                        }
                        if (support.support === 'no') {
                            if (version.version !== 'current') {
                                td.appendChild(document.createTextNode(' '));
                            }
                            nosupport = document.createElement('span');
                            nosupport.setAttribute('style', 'color: #f00;');
                            nosupport.appendChild(document.createTextNode('Not supported'));
                            td.appendChild(nosupport);
                        } else if (support.support !== 'yes' || (version.version === 'current')) {
                            td.appendChild(document.createTextNode(' (' + support.support + ')'));
                        }

                        // Prefix
                        if (support.prefix && support.prefix_mandatory) {
                            td.appendChild(document.createTextNode(' '));
                            prefix = document.createElement('code');
                            prefix.setAttribute('style', 'white-space: nowrap;');
                            prefix.appendChild(document.createTextNode(support.prefix));
                            td.appendChild(prefix);
                        } else {
                            prefix = null;
                        }

                        // Note
                        if (support.note) {
                            td.appendChild(document.createTextNode(' '));
                            noteNum = resources.meta.compat_table.notes[supportId];
                            noteId = 'wpc-compat-' + resources.data.id + '-note-' + noteNum;
                            noteSup = document.createElement('sup');
                            note = document.createElement('a');
                            note.setAttribute('id', noteId + '-back');
                            note.setAttribute('href', '#' + noteId);
                            note.appendChild(document.createTextNode("[" + noteNum + "]"));
                            noteSup.appendChild(note);
                            td.appendChild(noteSup);
                        } else {
                            note = null;
                        }
                    }
                } else {
                    unknown = document.createElement('span');
                    unknown.setAttribute('style', 'color: rgb(255, 153, 0);');
                    unknown.setAttribute('title', "Compatibility unknown; please update this.");
                    unknown.appendChild(document.createTextNode('?'));
                    td.appendChild(unknown);
                }
                tr.appendChild(td);
            }

            tbody.appendChild(tr);
        }

        // Recursively add children
        childCnt = feature.links.children.length;
        for (childIdx = 0; childIdx < childCnt; childIdx += 1) {
            childId = feature.links.children[childIdx];
            WPC.generate_browser_rows(childId, resources, lang, tab, tbody);
        }
    },
    strings: {
        'Basic support': {
            'de': 'Grundlegende Unterstützung',
            'en': 'Basic support',
            'es': 'Soporte básico',
            'fr': 'Support de base',
            'ja': '基本サポート',
            'pt-BR': 'Suporte básico',
        },
    }
};
