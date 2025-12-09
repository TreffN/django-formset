import pytest
from bs4 import BeautifulSoup

from django.test import Client, RequestFactory
from django.views.generic.edit import CreateView, UpdateView

from formset.views import FormViewMixin
from testapp.forms.leafletcollection import MapForm

@pytest.fixture(params=['bootstrap'])
# more parameters: (params=[None, 'bootstrap', 'bulma', 'foundation', 'tailwind', 'uikit'])
def framework(request):
    return request.param

@pytest.fixture
def create_view(framework):
    view_class = type('CreateView', (FormViewMixin, CreateView), {})
    return view_class.as_view(
        template_name='testapp/native-form.html',
        form_class=MapForm,
        extra_context={'framework': framework},
        success_url = '/success',
    )

@pytest.fixture
def native_soup(create_view):
    view_initkwargs = create_view.view_initkwargs
    framework = view_initkwargs['extra_context']['framework']
    url = f'/{framework}/map_form' if framework else '/default/map_form'
    request = RequestFactory().get(url)
    response = create_view(request)
    response.render()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup, framework

@pytest.mark.django_db
def test_render_map_form(native_soup):
    '''
        Tests if map form can be rendered
    '''
    soup, framework = native_soup
    django_formset = soup.find('django-formset')
    assert django_formset is not None
    django_leaflet = django_formset.find_all(attrs={"is": "django-leafletclient"})
    assert django_leaflet is not None
    # new
    # magic_mock = mocker.MagicMock()
    # page.expose_function('handle_initialized', lambda s: magic_mock(s))
    # page.evaluate('django_leaflet.dispatchEvent(new CustomEvent("leaflet-client-initialized", {}))')
    # assert  django_leaflet is not None

'''
Optionen für Karte:
    djoptions = {"srid": null, "extent": [[-90, -180], [90, 180]], "fitextent": true, "center": null, "zoom": null, "precision": 6, "minzoom": null, "maxzoom": null, "layers": [["OSM", "//tile.openstreetmap.org/{z}/{x}/{y}.png", "\u00a9 <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"]], "overlays": [], "attributionprefix": null, "scale": "metric", "minimap": false, "resetview": true, "tilesextent": []},
    options = {djoptions: djoptions, initfunc: loadmap,
               globals: false, callback: id_geometry_map_callback},
    map = L.Map.djangoMap('id_geometry-map', options);
'''

'''
Ablauf:
@pytest.mark.django_db
async def test_checkValidity_of_geometry(page, live_server):
    url = live_server.url + '/bootstrap/leafletcollection'
    await page.goto(url)

    # wait for initialization
    await page.wait_for_selector('django-formset [is="django-leafletclient"]')

    # initialize map and geometry
    await page.evaluate("""
        const map = L.map('map').setView([51.505, -0.09], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        const leafletClient = document.querySelector('[is="django-leafletclient"]');
        leafletClient.dispatchEvent(new CustomEvent('django-leaflet-client-on-map-ready', { detail: { map: map } }));

        const layer = L.polygon([
            [51.5, -0.09],
            [51.51, -0.08],
            [51.49, -0.07]
        ]).addTo(map);

        leafletClient[Object.getOwnPropertySymbols(leafletClient)[0]].drawnGeometries.addLayer(layer);
    """)

    result = await page.evaluate("""
        const leafletClient = document.querySelector('[is="django-leafletclient"]');
        return leafletClient.checkValidity();
    """)
    assert result is True
'''

# Vorlage:
# @pytest.mark.urls(__name__)
# @pytest.mark.parametrize('viewname', ['test_geometry_drawn'])
# def test_geometry_drawn(page, mocker, viewname):
#     magic_mock = mocker.MagicMock()
#     page.expose_function('handle_emit_4', lambda s: magic_mock(s))
#     page.evaluate('document.addEventListener("my_event", () => handle_emit_4("button_clicked"))')
#     page.click('django-formset button')
#     magic_mock.assert_called_with('button_clicked')
