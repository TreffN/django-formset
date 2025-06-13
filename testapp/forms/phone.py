from django.contrib.gis.forms import PointField, LineStringField, PolygonField, MultiPointField, MultiLineStringField, \
    MultiPolygonField, GeometryCollectionField, GeometryField, OSMWidget, OpenLayersWidget
from django.forms import fields, forms
from leaflet.forms.widgets import LeafletWidget

from formset.validators import phone_number_validator
from formset.widgets import PhoneNumberInput, LeafletClientWidget


class PhoneForm(forms.Form):
    """
    How to use the PhoneNumberInput widget.
    """
    phone_number = fields.CharField(
        label="Phone Number",
        validators=[phone_number_validator],
        widget=PhoneNumberInput,
    )

    mobile_number = fields.CharField(
        label="Mobile Number",
        initial='+43 664 1234567',
        validators=[phone_number_validator],
        widget=PhoneNumberInput(attrs={'default-country-code': 'at', 'mobile-only': True}),
    )

    custom_leaflet = PolygonField(
        widget=LeafletClientWidget()
    )

    # leaflet_map = MultiPointField(
    #     widget=LeafletWidget()
    # )

    # point_location = PointField(widget=OpenLayersWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': -52
    # }))

    # line_location = LineStringField()
    # polygon_location = PolygonField()
    # multi_point_location= MultiPointField()
    # multi_line_location = MultiLineStringField()
    # multi_polygon_location = MultiPolygonField()
    # geometry_collection = GeometryCollectionField()
    # geometry = GeometryField()
    #
    # osm_point_location = PointField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_line_location = LineStringField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_polygon_location = PolygonField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_multi_point_location= MultiPointField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_multi_line_location = MultiLineStringField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_multi_polygon_location = MultiPolygonField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_geometry_collection = GeometryCollectionField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
    # osm_geometry = GeometryField(widget=OSMWidget(attrs={
    #     'default_lon': 7,
    #     'default_lat': 52
    # }))
