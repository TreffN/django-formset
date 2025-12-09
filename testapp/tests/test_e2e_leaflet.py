import re
from time import sleep
import json
import pytest
from playwright.sync_api import expect

from django.urls import path

from formset.views import FormView, FormCollectionView
from .utils import get_javascript_catalog, ContextMixin
from testapp.forms.leafletcollection import MapForm
# for collections:
#from testapp.forms.leafletcollection import LeafletCollection

class DemoFormView(ContextMixin, FormView):
    template_name = 'testapp/native-form.html' #'../../formset/templates/formset/default/widgets/leaflet.html'
    success_url = '/success'


urlpatterns = [
    path('leaflet', DemoFormView.as_view(form_class=MapForm), name='leaflet'),
    get_javascript_catalog(),
]

# for collections:
# class FormCollectionViewTest(ContextMixin, FormCollectionView):
#     success_url='/success'
#
#
# urlpatterns = [
#     path('leaflet', FormCollectionViewTest.as_view(
#         collection_class=LeafletCollection,
#         template_name = 'testapp/form-collection.html',
#         extra_context = {
#             'click_actions': 'submit -> proceed',
#             'force_submission': True,
#         }
#     ), name='leaflet'),
#     get_javascript_catalog(),
#]

@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['leaflet'])
def test_leaflet_map_visible(page, viewname):
    django_leafletclient = page.locator('django-formset div[is="django-leafletclient"]')
    expect(django_leafletclient).to_be_visible()

    leaflet_map = page.locator('#id_geometry-map')
    expect(leaflet_map).to_be_visible()

    input_field = page.locator('input[name="caption"]')
    expect(input_field).to_be_visible()

    id_field = page.locator('input[name="id"]')
    expect(id_field).not_to_be_visible()

@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['leaflet'])
def test_leaflet_map_geom(page, mocker, viewname):
    '''
        LeafletCLientElement.getGeometryCollection() should be tested
    '''
    django_leafletclient = page.locator('django-formset div[is="django-leafletclient"]')
    #leaflet_container = page.locator('#id_geometry-map')
    marker_icon = page.locator('img.leaflet-marker-icon')
    page.screenshot(path="start.png")
    expect(marker_icon).not_to_be_visible()

    page.click('a.leaflet-draw-draw-marker')
    marker_button = page.locator('.leaflet-draw-draw-marker.leaflet-draw-toolbar-button-enabled')
    expect(marker_button).to_have_class(re.compile("enabled"))

    page.mouse.click(500, 200)
    #leaflet_container.click(position={"x": 100,"y": 100})#{"x": 6.940613,"y": 50.754704})
    page.screenshot(path="marker.png")

    expect(marker_icon).to_be_visible()
    #django_leafletclient.evaluate("elem => elem.dispatchEvent(new CustomEvent('django-leaflet-drawn'))")
    # check if triggered
    was_triggered = page.evaluate("""
      () => {
        const el = document.querySelector('django-formset div[is="django-leafletclient"]');
        let triggered = false;

        const orig = el.dispatchEvent;
        el.dispatchEvent = function(evt) {
          if (evt.type === 'django-leaflet-drawn') {
            triggered = true;
          }
          return orig.call(this, evt);
        };

        el.dispatchEvent(new CustomEvent('django-leaflet-drawn'));
        return triggered;
      }
    """)

    assert was_triggered is True

    spy = mocker.spy(DemoFormView, 'post')
    page.locator('django-formset').evaluate('elem => elem.submit()')
    sleep(0.2)
    spy.assert_called()
    assert spy.spy_return.status_code == 200
    request = json.loads(spy.call_args.args[1].body)
    print(request)

    # TODO
    #geometry = page.locator('textarea[name="geometry"]')
    #expect(geometry).not_to_be_empty()

    assert "Point" in request["formset_data"]["geometry"]

    '''
    Screenshots vergleichen:
    pip install pillow

    from PIL import Image, ImageChops

    def compare_screenshots(img1_path, img2_path, diff_path='diff.png'):
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        diff = ImageChops.difference(img1, img2)

        if diff.getbbox():
            diff.save(diff_path)
            return False  # Bilder sind unterschiedlich
        return True  # Bilder sind identisch

    assert compare_screenshots("debug1.png", "debug2.png"), "Screenshots differ!"
    '''

@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['leaflet'])
def test_caption_input(page, mocker, viewname):
    input_test_string = 'Umriss'
    input_field = page.locator('input[name="caption"]')
    input_field.fill(input_test_string)
    input_field.evaluate('elem => elem.blur()')
    spy = mocker.spy(DemoFormView, 'post')
    page.locator('django-formset').evaluate('elem => elem.submit()')
    sleep(0.2)
    spy.assert_called()
    assert spy.spy_return.status_code == 200
    request = json.loads(spy.call_args.args[1].body)
    assert request['formset_data']['caption'] == input_test_string
