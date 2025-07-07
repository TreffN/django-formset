from django.forms import fields, widgets
from django.forms.models import ModelForm

from formset.collection import FormCollection
from formset.widgets import LeafletClientWidget

from testapp.models.leaflet import LeafletMap, Leaflet


class MapForm(ModelForm):

    id = fields.IntegerField(
        required=False,
        widget=widgets.HiddenInput,
    )

    class Meta:
        model = LeafletMap
        fields = ['id', 'geometry', 'caption']
        widgets = {
            'geometry': LeafletClientWidget(
                  attrs={
                      'settings_overrides': {
                          'DEFAULT_CENTER': (50.7, 7.0),
                          'DEFAULT_ZOOM': 10,
                      }
                 #     'loadevent': 'load',
                      }
            )
        }


class LeafletMapCollection(FormCollection):
    min_siblings = 0
    extra_siblings = 1
    leafletmap = MapForm()
    legend = "Leaflet Maps"
    add_label = "Add Leaflet Maps"
    related_field = 'leaflet'

    def retrieve_instance(self, data):
        if data := data.get('leafletmap'):
            try:
                return self.instance.leafletmaps.get(id=data.get('id') or 0)
            except (AttributeError, LeafletMap.DoesNotExist, ValueError):
                return LeafletMap(geometry=data.get('geometry'), leaflet=self.instance)

class LeafletForm(ModelForm):
    class Meta:
        model = Leaflet
        fields = '__all__'


class LeafletCollection(FormCollection):
    leaflet = LeafletForm()
    leafletmaps = LeafletMapCollection()

