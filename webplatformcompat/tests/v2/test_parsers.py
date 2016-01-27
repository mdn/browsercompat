# -*- coding: utf-8 -*-
"""Tests for JSON API v1.0 parser."""
from __future__ import unicode_literals
from json import dumps

from django.utils.six import BytesIO
from rest_framework.exceptions import ParseError

from .base import TestCase
from webplatformcompat.serializers import FeatureSerializer
from webplatformcompat.v2.parsers import JsonApiV10Parser


class TestJsonApiV10Parser(TestCase):
    def parse(self, data, as_relationship=None):
        stream = BytesIO(dumps(data).encode('utf8'))
        parser = JsonApiV10Parser()
        context = {
            'fields_extra': FeatureSerializer.get_fields_extra(),
            'as_relationship': as_relationship,
        }
        return parser.parse(stream, None, context)

    def test_simple(self):
        resource = self.parse({
            'data': {
                'type': 'features',
                'id': '1',
                'attributes': {
                    'slug': 'the_feature',
                    'name': {'en': 'The Feature'},
                },
                'relationships': {
                    'parent': {
                        'data': {
                            'type': 'features', 'id': None,
                        },
                    },
                    'children': {
                        'data': [
                            {'type': 'features', 'id': '2'},
                            {'type': 'features', 'id': '3'},
                        ],
                    },
                },
            }
        })
        expected = {
            'id': '1',
            'slug': 'the_feature',
            'name': {'en': 'The Feature'},
            'parent': None,
            'children': ['2', '3'],
        }
        self.assertDataEqual(resource, expected)

    def test_complex(self):
        resource = self.parse({
            'data': {
                'id': '1',
                'type': 'features',
                'attributes': {
                    'slug': 'the_feature',
                    'name': {'en': 'The Feature'},
                },
                'relationships': {
                    'parent': {
                        'data': {'type': 'features', 'id': None},
                    },
                    'children': {
                        'data': [
                            {'type': 'features', 'id': '2'},
                            {'type': 'features', 'id': '3'},
                        ]
                    },
                }
            },
            'included': [
                {
                    'id': '2',
                    'type': 'features',
                    'attributes': {
                        'slug': 'child2',
                        'name': {'en': 'Child 2'},
                    },
                    'relationships': {
                        'parent': {
                            'data': {'type': 'features', 'id': '1'},
                        },
                    },
                }, {
                    'id': '3',
                    'type': 'features',
                    'attributes': {
                        'slug': 'child3',
                        'name': {'en': 'Child 3'},
                    },
                    'relationships': {
                        'parent': {
                            'data': {'type': 'features', 'id': '1'},
                        }
                    },
                },
            ],
            'meta': {
                'foo': 'bar'
            },
            'other': {
                'ignored': 'yep'
            }
        })
        expected = {
            'id': '1',
            'slug': 'the_feature',
            'name': {'en': 'The Feature'},
            'parent': None,
            'children': ['2', '3'],
            '_view_extra': {
                'features': [
                    {
                        'id': '2',
                        'slug': 'child2',
                        'name': {'en': 'Child 2'},
                        'parent': '1',
                    }, {
                        'id': '3',
                        'slug': 'child3',
                        'name': {'en': 'Child 3'},
                        'parent': '1',
                    }],
                'meta': {'foo': 'bar'},
            }
        }
        self.assertDataEqual(resource, expected)

    def test_duplicate_in_attribute_and_relationships(self):
        data = {
            'data': {
                'id': '139',
                'type': 'features',
                'attributes': {
                    'parent': None,
                },
                'relationships': {
                    'parent': {
                        'data': {'type': 'feature', 'id': None},
                    }
                },
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = (
            '"parent" can not be in both data.attributes and'
            ' data.relationships.')
        self.assertEqual(str(pe.exception), expected_msg)

    def test_view_extra_in_attributes(self):
        data = {
            'data': {
                'id': '161',
                'type': 'features',
                'attributes': {
                    '_view_extra': 'foo'
                },
            },
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = (
            '"_view_extra" is not allowed in data.attributes.')
        self.assertEqual(str(pe.exception), expected_msg)

    def test_meta_in_relationships(self):
        data = {
            'data': {
                'id': '177',
                'type': 'features',
                'relationships': {
                    'meta': {
                        'data': {'type': 'features', 'id': '_meta'},
                    }
                }
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = '"meta" is not allowed in data.relationships.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_id_is_optional(self):
        """Test that 'id' can be omitted.

        For example, id is omitted when creating a resource.
        """
        resource = self.parse({
            'data': {
                'type': 'features',
                'attributes': {
                    'slug': 'the_feature',
                    'name': {'en': 'The Feature'},
                },
            }
        })
        expected = {
            'slug': 'the_feature',
            'name': {'en': 'The Feature'},
        }
        self.assertDataEqual(resource, expected)

    def test_omit_main_type(self):
        data = {
            'data': {
                'id': '1'
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = 'data.type is required.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_wrong_main_type(self):
        data = {
            'data': {
                'id': '1',
                'type': 'feature',
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = 'data.type should be "features", is "feature".'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_just_meta(self):
        # Valid but useless JSON API v1.0 document
        resource = self.parse({
            'meta': {
                'foo': 'bar',
            },
        })
        expected = {
            '_view_extra': {
                'meta': {
                    'foo': 'bar',
                },
            },
        }
        self.assertDataEqual(resource, expected)

    def test_omit_relationship_type(self):
        data = {
            'data': {
                'id': '1',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {'id': None}
                    }
                }
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = 'data.relationships.parent.data.type is required.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_omit_relationship_id(self):
        data = {
            'data': {
                'id': '1',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {}
                    }
                }
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = 'data.relationships.parent.data.id is required.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_wrong_relationship_type(self):
        data = {
            'data': {
                'id': '1',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {'type': 'feature', 'id': '7'}
                    }
                }
            }
        }

        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = (
            'data.relationships.parent.data.type should be "features",'
            ' is "feature".')
        self.assertEqual(str(pe.exception), expected_msg)

    def test_as_relationship(self):
        resource = self.parse({
            'data': {'type': 'features', 'id': '7'}
        }, as_relationship='parent')
        expected = {
            'parent': '7'
        }
        self.assertEqual(resource, expected)

    def test_as_relationship_omit_type_fails(self):
        data = {'data': {'id': '7'}}
        with self.assertRaises(ParseError) as pe:
            self.parse(data, as_relationship='parent')
        expected_msg = 'data.type is required.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_complex_error(self):
        data = {
            'data': {
                'id': '1',
                'type': 'features',
                'attributes': {
                    'name': {'en': 'The Feature'},
                },
            },
            'included': [
                {
                    'id': '2',
                    'attributes': {
                        'slug': 'child2',
                        'name': {'en': 'Child 2'},
                    },
                    'relationships': {
                        'parent': {
                            'data': {'type': 'features', 'id': '1'},
                        },
                    },
                },
            ],
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = 'included.0.type is required.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_clear_parent_by_null_data(self):
        resource = self.parse({
            'data': {
                'id': '352',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': None,
                    }
                }
            }
        })
        expected = {
            'id': '352',
            'parent': None
        }
        self.assertEqual(resource, expected)

    def test_clear_parent_by_null_id(self):
        resource = self.parse({
            'data': {
                'id': '370',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'data': {'type': 'features', 'id': None},
                    }
                }
            }
        })
        expected = {
            'id': '370',
            'parent': None
        }
        self.assertEqual(resource, expected)

    def test_relationship_without_data(self):
        data = {
            'data': {
                'id': '388',
                'type': 'features',
                'relationships': {
                    'parent': {
                        'not-data': []
                    }
                }
            }
        }
        with self.assertRaises(ParseError) as pe:
            self.parse(data)
        expected_msg = '"data" is required in data.relationships.parent.'
        self.assertEqual(str(pe.exception), expected_msg)

    def test_implied_resource_type(self):
        """Test that no 'resource' in fields_extra uses the name as type."""
        resource = self.parse({
            'data': {
                'id': '406',
                'type': 'features',
                'relationships': {
                    'sections': {
                        'data': [
                            {'type': 'sections', 'id': '101'}
                        ]
                    }
                }
            }
        })
        expected = {'id': '406', 'sections': ['101']}
        self.assertEqual(resource, expected)

    def test_unknown_relationship(self):
        """Unknown relationhips are parsed without verification."""
        resource = self.parse({
            'data': {
                'id': '424',
                'type': 'features',
                'relationships': {
                    'future': {
                        'data': [
                            {'type': 'future', 'id': '2016'}
                        ]
                    }
                }
            }
        })
        expected = {'id': '424', 'future': ['2016']}
        self.assertEqual(resource, expected)
