""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.utils import unittest
from django.test.client import Client
from django.conf import settings
from os.path import abspath, dirname
from spotseeker_server.models import Spot, SpotImage
from django.core.files import File
from PIL import Image
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
class SpotResourceImageTest(unittest.TestCase):

    def setUp(self):
        spot = Spot.objects.create(name="This is to test images in the spot resource")
        self.spot = spot

        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = SpotImage.objects.create(description="This is the GIF test", spot=spot, image=File(f))
        f.close()

        self.gif = gif

        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = SpotImage.objects.create(description="This is the JPEG test", spot=spot, image=File(f))
        f.close()

        self.jpeg = jpeg

        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = SpotImage.objects.create(description="This is the PNG test", spot=spot, image=File(f))
        f.close()

        self.png = png

    def test_empty_image_data(self):
        dummy_cache = cache.get('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            spot = Spot.objects.create(name="A spot with no images")

            c = Client()
            response = c.get('/api/v1/spot/{0}'.format(spot.pk))
            spot_dict = json.loads(response.content)

            self.assertEquals(len(spot_dict["images"]), 0, "Has an empty array for a spot w/ no images")

    def test_image_data(self):
        dummy_cache = cache.get('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get('/api/v1/spot/{0}'.format(self.spot.pk))

            spot_dict = json.loads(response.content)

            self.assertEquals(len(spot_dict["images"]), 3, "Has 3 images")

            has_gif = False
            has_png = False
            has_jpg = False
            for image in spot_dict["images"]:
                if image["id"] == self.gif.pk:
                    has_gif = True
                    self.assertEquals(image["url"], "/api/v1/spot/{0}/image/{1}".format(self.spot.pk, self.gif.pk))
                    self.assertEquals(image["thumbnail_root"], "/api/v1/spot/{0}/image/{1}/thumb".format(self.spot.pk, self.gif.pk))
                    self.assertEquals(image["content-type"], "image/gif")
                    img = Image.open("%s/../resources/test_gif.gif" % TEST_ROOT)
                    self.assertEquals(image["width"], img.size[0], "Includes the gif width")
                    self.assertEquals(image["height"], img.size[1], "Includes the gif height")
                    self.assertEquals(image["creation_date"], image["modification_date"], "Has the same modification and creation date")
                    self.assertEquals(image["upload_user"], "", "Lists an empty upload user")
                    self.assertEquals(image["upload_application"], "", "Lists an empty upload application")

                if image["id"] == self.png.pk:
                    has_png = True
                    self.assertEquals(image["url"], "/api/v1/spot/{0}/image/{1}".format(self.spot.pk, self.png.pk))
                    self.assertEquals(image["thumbnail_root"], "/api/v1/spot/{0}/image/{1}/thumb".format(self.spot.pk, self.png.pk))
                    self.assertEquals(image["content-type"], "image/png")
                    img = Image.open("%s/../resources/test_png.png" % TEST_ROOT)
                    self.assertEquals(image["width"], img.size[0], "Includes the png width")
                    self.assertEquals(image["height"], img.size[1], "Includes the png height")
                    self.assertEquals(image["creation_date"], image["modification_date"], "Has the same modification and creation date")
                    self.assertEquals(image["upload_user"], "", "Lists an empty upload user")
                    self.assertEquals(image["upload_application"], "", "Lists an empty upload application")

                if image["id"] == self.jpeg.pk:
                    has_jpg = True
                    self.assertEquals(image["url"], "/api/v1/spot/{0}/image/{1}".format(self.spot.pk, self.jpeg.pk))
                    self.assertEquals(image["thumbnail_root"], "/api/v1/spot/{0}/image/{1}/thumb".format(self.spot.pk, self.jpeg.pk))
                    self.assertEquals(image["content-type"], "image/jpeg")
                    img = Image.open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                    self.assertEquals(image["width"], img.size[0], "Includes the jpeg width")
                    self.assertEquals(image["height"], img.size[1], "Includes the jpeg height")
                    self.assertEquals(image["creation_date"], image["modification_date"], "Has the same modification and creation date")
                    self.assertEquals(image["upload_user"], "", "Lists an empty upload user")
                    self.assertEquals(image["upload_application"], "", "Lists an empty upload application")

            self.assertEquals(has_gif, True, "Found the gif")
            self.assertEquals(has_jpg, True, "Found the jpg")
            self.assertEquals(has_png, True, "Found the png")
