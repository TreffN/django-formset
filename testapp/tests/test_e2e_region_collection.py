import re
from time import sleep
import json
import pytest
from playwright.sync_api import expect

from django.urls import path

from .utils import get_javascript_catalog, ContextMixin
from formset.views import FormCollectionView
from testapp.forms.regioncollection import RegionCollection

class FormCollectionView(ContextMixin, FormCollectionView):
    success_url='/success'

urlpatterns = [
    path('regioncollection', FormCollectionView.as_view(
        collection_class=RegionCollection,
        template_name='testapp/form-collection.html',
        extra_context={'click_actions': 'submit -> proceed', 'force_submission': True},
    ), name='regioncollection'),
    get_javascript_catalog(),
]

@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['regioncollection'])
def test_elements_visible(page, viewname):
    django_leafletclient = page.locator('django-formset div[is="django-leafletclient"]')
    expect(django_leafletclient).to_be_visible()

    leaflet_map = page.locator('#id_regionmaps0regionmapgeometry-map')
    expect(leaflet_map).to_be_visible()

    input_field = page.locator('input[name="caption"]')
    expect(input_field).to_be_visible()

    id_field = page.locator('input[name="id"]')
    expect(id_field).not_to_be_visible()

@pytest.mark.urls(__name__)
@pytest.mark.parametrize('viewname', ['regioncollection'])
def test_submit_region_collection(page, mocker, viewname):
    page.screenshot(path="start.png")
    spy = mocker.spy(FormCollectionView, 'post')

    collection_name= page.locator('input[id="id_region.name"]')
    expect(collection_name).to_be_visible()
    collection_name.fill('Regions')

    page.click('a.leaflet-draw-draw-rectangle')
    rectangle_button = page.locator('.leaflet-draw-draw-rectangle.leaflet-draw-toolbar-button-enabled')
    expect(rectangle_button).to_have_class(re.compile("enabled"))
    page.mouse.move(500,200)
    page.mouse.down()
    page.mouse.move(550, 250)
    page.mouse.up()
    page.screenshot(path="marker.png")

    caption = page.locator('input[id="id_regionmaps.0.regionmap.caption"]')
    expect(caption).to_be_visible()
    caption.fill('Region')
    page.screenshot(path="caption.png")

    submit_button = page.locator('button:has-text("Submit")')
    expect(submit_button).to_be_visible()
    expect(submit_button).to_be_enabled()
    submit_button.click()
    request = json.loads(spy.call_args.args[1].body)
    expected = {
        'formset_data': {
            'regionmaps': [{
                'regionmap': {
                    'geometry': '{"type":"Polygon","coordinates":[[[6.807404,50.74167],[6.807404,50.785102],[6.876068,50.785102],[6.876068,50.74167],[6.807404,50.74167]]]}',
                    'caption': 'Region',
                    'id': ''
                }}],
            'region': {
                'name': 'Regions'
            }}}

    assert "Polygon" in request["formset_data"]["regionmaps"][0]["regionmap"]["geometry"]
    assert request == expected
    sleep(0.2)
    spy.assert_called()
    assert spy.spy_return.status_code == 200
