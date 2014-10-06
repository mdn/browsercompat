window.Browse = Ember.Application.create({
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

Browse.Router.map(function() {
    this.resource('browsers');
    this.resource('browser', {path: '/browsers/:browser_id'});
    this.resource('features');
});

/* Serializer - JsonApiSerializer with modifictions */
DS.JsonApiNamespacedSerializer = DS.JsonApiSerializer.extend({
    namespace: 'api/v1',
    extractLinks: function(links) {
        // Modifications:
        // Strip the namespace from links as well
        // Camelize linkKeys
        var link, key, value, route;
        var extracted = [], linkEntry, linkKey;

        for (link in links) {
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
            if (route.indexOf(this.namespace) == 0) {
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
            DS._routes[linkKey] = route;
        }

        return extracted;
    }
})

/* Adapter - JsonApiAdapter with modifictions */
Browse.ApplicationAdapter = DS.JsonApiAdapter.extend({
    namespace: 'api/v1',
    defaultSerializer: 'DS/jsonApiNamespaced'
/*
    buildURL: function(typeName, id) {
        var x = this._super(typeName, id);
        //debugger;
        return x;
    }
*/
});
//DS._routes['browserVersion'] = "versions/{browsers.versions}"


/* Routes */
Browse.BrowsersRoute = Ember.Route.extend({
    model: function() {
        return this.store.find('browser');
    }
});

Browse.FeaturesRoute = Ember.Route.extend({
    model: function() {
        return this.store.find('feature');
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
});

Browse.Version = DS.Model.extend({
    browser: DS.belongsTo('browser'),
    version: attr('string'),
    release_day: attr('date'),
    retirement_day: attr('date'),
    status: attr('string'),
    release_notes_uri: attr(),
    note: attr(),
    order: attr('number')
});

/* Controllers */
Browse.BrowserController = Ember.ObjectController.extend({
    versionInflection: function() {
        var versions = this.get('model.versions');
        var count = versions.get('length');
        if (count === 1) {
            return 'Version';
        } else {
            return 'Versions';
        }
    }.property('model.versions.@each')
});
