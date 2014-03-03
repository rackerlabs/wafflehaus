# Copyright 2013 Openstack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

import webob.dec
import webob.exc

import wafflehaus.resource_filter as rf


class BlockResource(object):

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.log.info('Starting wafflehaus resource blocker middleware')
        self.user_id = conf.get('user_id')
        self.testing = (conf.get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.resources = rf.parse_resources(conf.get('resource'))

    @webob.dec.wsgify
    def __call__(self, req):
        if rf.matched_request(req, self.resources):
            return webob.exc.HTTPForbidden()
        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def block_resource(app):
        return BlockResource(app, conf)
    return block_resource