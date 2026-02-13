from django.forms import fields, widgets
from django.forms.models import ModelForm

from formset.collection import FormCollection
from formset.widgets import LeafletClientWidget

from testapp.models.region import RegionMap, Region


class MapForm(ModelForm):

    id = fields.IntegerField(
        required=False,
        widget=widgets.HiddenInput,
    )

    class Meta:
        model = RegionMap
        fields = ['id', 'geometry', 'caption']
        widgets = {
            'geometry': LeafletClientWidget(
                  attrs={
                      'settings_overrides': {
                          'DEFAULT_CENTER': (50.7, 7.0),
                          'DEFAULT_ZOOM': 10,
                      },
                      'wms': {
                          'url': 'https://ows.terrestris.de/osm/service?',
                          'config': {
                              'layers': 'OSM-Overlay-WMS',
                              'format': 'image/png',
                              'transparent': True,
                              'attribution': '© terrestris GmbH & Co. KG',
                          }
                      }
                  }
            )
        }


class RegionMapCollection(FormCollection):
    min_siblings = 0
    extra_siblings = 1
    regionmap = MapForm()
    legend = "Region Maps"
    add_label = "Add Region Maps"
    related_field = 'region'

    def retrieve_instance(self, data):
        if data := data.get('regionmap'):
            try:
                return self.instance.regionmaps.get(id=data.get('id') or 0)
            except (AttributeError, RegionMap.DoesNotExist, ValueError):
                return RegionMap(geometry=data.get('geometry'), region=self.instance)

class RegionForm(ModelForm):
    class Meta:
        model = Region
        fields = '__all__'


class RegionCollection(FormCollection):
    region = RegionForm()
    regionmaps = RegionMapCollection()

