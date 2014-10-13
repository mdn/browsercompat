"use strict";
/*global Browse: false, DS: false, Ember: false, window: false */
window.Browse = Ember.Application.create({
    // Debugging flags
    LOG_TRANSITIONS: true,
    LOG_TRANSITIONS_INTERNAL: false,
    LOG_ACTIVE_GENERATION: false,
    LOG_RESOLVER: false
});

/* Router */
Browse.Router.reopen({
    rootURL: '/browse/',
    location: 'history'
});

Browse.Router.map(function () {
    this.resource('browsers');
    this.resource('browser', {path: '/browsers/:browser_id'});
    this.resource('versions');
    this.resource('version', {path: '/versions/:version_id'});
    this.resource('features');
    this.resource('feature', {path: '/features/:feature_id'});
});

/* Serializer - JsonApiSerializer with modifictions */
DS.JsonApiNamespacedSerializer = DS.JsonApiSerializer.extend({
    namespace: 'api/v1',
    extractLinks: function (links) {
        // Modifications:
        // Strip the namespace from links as well
        // Camelize linkKeys
        var link, key, value, route, extracted = [], linkEntry, linkKey;

        for (link in links) {
            if (links.hasOwnProperty(link)) {
                key = link.split('.').pop();
                value = links[link];
                if (typeof value === 'string') {
                    route = value;
                } else {
                    key = value.type || key;
                    route = value.href;
                }

                // strip base url
                if (route.substr(0, 4).toLowerCase() === 'http') {
                    route = route.split('//').pop().split('/').slice(1).join('/');
                }

                // strip prefix slash
                if (route.charAt(0) === '/') {
                    route = route.substr(1);
                }

                // strip namespace
                if (route.indexOf(this.namespace) === 0) {
                    route = route.substr(this.namespace.length);
                    if (route.charAt(0) === '/') {
                        route = route.substr(1);
                    }
                }

                linkEntry = { };
                linkKey = Ember.String.singularize(key);
                linkKey = Ember.String.camelize(linkKey);
                linkEntry[linkKey] = route;
                extracted.push(linkEntry);
                /*jslint nomen: true */
                /* DS._routes is convention of DS.JsonApiSerializer */
                DS._routes[linkKey] = route;
                /*jslint nomen: false */
            }
        }

        return extracted;
    },
    extractMeta: function (store, type, payload) {
        if (payload && payload.meta) {
            store.metaForType(type, payload.meta);
            delete payload.meta;
        }
    },
});

/* Adapter - JsonApiAdapter with modifictions */
Browse.ApplicationAdapter = DS.JsonApiAdapter.extend({
    namespace: 'api/v1',
    defaultSerializer: 'DS/jsonApiNamespaced'
});


/* Routes */
Browse.PaginatedRouteMixin = Ember.Mixin.create({
    queryParams: {
        page: {refreshModel: true},
    },
    setupController: function (controller, model) {
        controller.set('model', model);
        controller.updatePagination();
    },
});

Browse.BrowsersRoute = Ember.Route.extend(Browse.PaginatedRouteMixin, {
    model: function () {
        return this.store.find('browser');
    }
});

Browse.VersionsRoute = Ember.Route.extend(Browse.PaginatedRouteMixin, {
    model: function () {
        return this.store.find('version');
    }
});

Browse.FeaturesRoute = Ember.Route.extend(Browse.PaginatedRouteMixin, {
    model: function () {
        return this.store.find('feature');
    }
});

Browse.SupportsRoute = Ember.Route.extend(Browse.PaginatedRouteMixin, {
    model: function () {
        return this.store.find('support');
    }
});

/* Models */
var attr = DS.attr;

Browse.Browser = DS.Model.extend({
    slug: attr('string'),
    icon: attr(),
    name: attr(),
    note: attr(),
    versions: DS.hasMany('version', {async: true}),
});

Browse.Feature = DS.Model.extend({
    slug: attr('string'),
    mdn_path: attr('string'),
    experimental: attr(),
    standardized: attr(),
    stable: attr(),
    obsolete: attr(),
    name: attr(),
    parent: DS.belongsTo('feature', {inverse: 'children', async: true}),
    children: DS.hasMany('feature', {inverse: 'parent', async: true}),
    supports: DS.hasMany('support', {async: true})
});

Browse.Version = DS.Model.extend({
    browser: DS.belongsTo('browser'),
    version: attr('string'),
    release_day: attr('date'),
    retirement_day: attr('date'),
    status: attr('string'),
    release_notes_uri: attr(),
    note: attr(),
    order: attr('number'),
    supports: DS.hasMany('support', {async: true})
});

Browse.Support = DS.Model.extend({
    support: attr('string'),
    prefix: attr('string'),
    prefix_mandatory: attr(),
    alternate_name: attr('string'),
    alternate_mandatory: attr(),
    requires_config: attr('string'),
    default_config: attr('string'),
    note: attr(),
    footnote: attr(),
    version: DS.belongsTo('version', {async: true}),
    feature: DS.belongsTo('feature', {async: true})
});

/* Controllers */

/* LoadMoreMixin based on https://github.com/pangratz/dashboard/commit/68d1728 */
Browse.LoadMoreMixin = Ember.Mixin.create(Ember.Evented, {
    loadingMore: false,
    currentPage: 1,
    resetLoadMore: function () {
        this.set('currentPage', 1);
    },
    pagination: null,
    canLoadMore: Ember.computed('pagination', 'model.length', function () {
        var pagination = this.get('pagination');
        return (pagination && pagination.next && pagination.count > this.get("model.length"));
    }),
    updatePagination: function () {
        var store = this.get('store'),
            modelType = this.get('model.type'),
            modelSingular = modelType.typeKey,
            modelPlural = Ember.String.pluralize(modelSingular),
            metadata = store.typeMapFor(modelType).metadata,
            pagination = metadata && metadata.pagination && metadata.pagination[modelPlural];
        this.set("pagination", pagination);
        this.set("loadingMore", false);
    },
    loadMore: function () {
        if (this.get('canLoadMore')) {
            var page = this.incrementProperty('currentPage'),
                self = this,
                modelSingular = this.get('model.type.typeKey'),
                results = this.get('store').findQuery(modelSingular, {page: page});
            this.set("loadingMore", true);
            results.then(function (newRecords) {
                self.updatePagination(newRecords);
            });
            return results;
        }
    },
    actions: {
        loadMore: function () { this.loadMore(); }
    }
});

Browse.Properties = {
    IdCounter: function (relation) {
        /* This property uses the private "data" method to count the number of
         * IDs.  The alternative, "models.<relation>.length", will load each
         * related instance from the API before returning a count.  This can
         * make list views slow and makes unneccessary API calls.  The caveat
         * is we're using a private method that may go away in the future.
         * However, Ember devs are opposed to a performant count for this use
         * case: https://github.com/emberjs/data/issues/586
        */
        return Ember.computed('model.data', function () {
            return this.get('model.data.' + relation + '.length');
        });
    },
};

Browse.BrowsersController = Ember.ArrayController.extend(Browse.LoadMoreMixin);

Browse.BrowserController = Ember.ObjectController.extend(Browse.LoadMoreMixin, {
    versionCount: Browse.Properties.IdCounter('versions'),
    versionCountText: Ember.computed('versionCount', function () {
        var count = this.get('versionCount');
        if (count === 1) { return '1 Version'; }
        return count + ' Versions';
    })
});

Browse.VersionsController = Ember.ArrayController.extend(Browse.LoadMoreMixin);

Browse.VersionController = Ember.ObjectController.extend(Browse.LoadMoreMixin, {
    featureCount: Browse.Properties.IdCounter('supports'),
    featureCountText: Ember.computed('featureCount', function () {
        var count = this.get('featureCount');
        if (count === 1) { return '1 Feature'; }
        return count + ' Features';
    }),
});

Browse.FeaturesController = Ember.ArrayController.extend(Browse.LoadMoreMixin);

Browse.FeatureController = Ember.ObjectController.extend(Browse.LoadMoreMixin, {
    featureNameHTML: Ember.computed('model.name', function () {
        var name = this.get('model.name');
        if (name.en) { return name.en; }
        if (name) { return "<code>" + name + "</code>"; }
        return "<em>none</em>";
    }),
    versionCount: Browse.Properties.IdCounter('supports'),
    versionCountText: Ember.computed('versionCount', function () {
        var count = this.get('versionCount');
        if (count === 1) { return '1 Version'; }
        return count + ' Versions';
    }),
});
