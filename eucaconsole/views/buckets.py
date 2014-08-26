# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Eucalyptus Object Store and AWS S3 Buckets

"""
import mimetypes

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..i18n import _
from ..views import LandingPageView, JSONResponse
from . import boto_error_handler


class BucketsView(LandingPageView):
    """Views for Buckets landing page"""
    VIEW_TEMPLATE = '../templates/buckets/buckets.pt'

    def __init__(self, request):
        super(BucketsView, self).__init__(request)
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/buckets'
        self.location = self.get_redirect_location('buckets')
        self.render_dict = dict(
            prefix=self.prefix,
        )

    @view_config(route_name='buckets', renderer=VIEW_TEMPLATE)
    def buckets_landing(self):
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='bucket_name', name=_(u'Bucket name: A to Z')),
            dict(key='-bucket_name', name=_(u'Bucket name: Z to A')),
        ]
        self.render_dict.update(
            initial_sort_key='bucket_name',
            json_items_endpoint=self.get_json_endpoint('buckets_json'),
            sort_keys=self.sort_keys,
            filter_fields=False,
            filter_keys=['name'],
        )
        return self.render_dict


class BucketsJsonView(LandingPageView):
    def __init__(self, request):
        super(BucketsJsonView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')

    @view_config(route_name='buckets_json', renderer='json', request_method='POST')
    def buckets_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        buckets = []
        with boto_error_handler(self.request):
            items = self.get_items()
            for item in items:
                bucket_name = item.name
                buckets.append(dict(
                    bucket_name=bucket_name,
                    bucket_contents_url=self.request.route_path('bucket_contents', name=bucket_name),
                    object_count=0,  # TODO: Implement object count via XHR fetch
                    owner='me',
                    creation_date=item.creation_date
                ))
            return dict(results=buckets)

    def get_items(self):
        return self.s3_conn.get_all_buckets() if self.s3_conn else []


class BucketContentsView(LandingPageView):
    """Views for actions on single bucket"""
    VIEW_TEMPLATE = '../templates/buckets/bucket_contents.pt'

    def __init__(self, request):
        super(BucketContentsView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.prefix = '/buckets'
        self.bucket_name = request.matchdict.get('name')
        self.render_dict = dict(
            bucket_name=self.bucket_name,
        )

    @view_config(route_name='bucket_contents', renderer=VIEW_TEMPLATE)
    def bucket_contents(self):
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='-size', name=_(u'Size: Largest to smallest')),
            dict(key='size', name=_(u'Size: Smallest to largest')),
        ]
        json_route_path = self.request.route_path('bucket_contents_json', name=self.bucket_name)
        self.render_dict.update(
            prefix=self.prefix,
            initial_sort_key='name',
            json_items_endpoint=self.get_json_endpoint(json_route_path, path=True),
            sort_keys=self.sort_keys,
            filter_fields=False,
            filter_keys=['name', 'size'],
        )
        return self.render_dict

    @staticmethod
    def get_bucket(request, s3_conn, bucket_name=None):
        with boto_error_handler(request):
            bucket_name = bucket_name or request.matchdict.get('name')
            bucket = s3_conn.lookup(bucket_name) if bucket_name else None
            if bucket is None:
                return HTTPNotFound()
            return bucket

    @staticmethod
    def get_icon_class(key_name):
        """Get the icon class from the mime type of an object based on its key name
        :returns a string that maps to a Foundation Icon Fonts 3 class name
        :rtype str
        See http://zurb.com/playground/foundation-icon-fonts-3

        """
        mime_type = mimetypes.guess_type(key_name)[0]
        if mime_type is None:
            return ''
        if '/' in key_name:
            key_name = key_name.split('/')[-1]
            mime_type = mimetypes.guess_type(key_name)[0]
        if '/' in mime_type:
            mime_type = mime_type.split('/')[0]
        icon_mapping = {
            'image': 'fi-photo',
            'text': 'fi-page',
        }
        return icon_mapping.get(mime_type, 'page')


class BucketContentsJsonView(LandingPageView):
    def __init__(self, request):
        super(BucketContentsJsonView, self).__init__(request)
        self.s3_conn = self.get_connection(conn_type='s3')
        self.bucket = BucketContentsView.get_bucket(request, self.s3_conn)

    @view_config(route_name='bucket_contents_json', renderer='json', request_method='POST')
    def bucket_contents_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        items = []
        for key in self.bucket.list():
            items.append(dict(
                name=key.name,
                size=key.size,
                is_folder=True if key.size == 0 else False,
                last_modified=key.last_modified,
                icon=BucketContentsView.get_icon_class(key.name),
            ))
        return dict(results=items)

