// Probleme bei Import: Uncaught TypeError: L.Map.djangoMap is not a function at loadmap
// import * as L from 'leaflet';
//import 'leaflet-draw';
//import 'leaflet-draw/dist/leaflet.draw.css';
//import L from 'leaflet';

import booleanValid from '@turf/boolean-valid';
import { Layer } from 'leaflet';

class LeafletClientField {
  private readonly divElement: HTMLDivElement;
  private map: L.Map | undefined;
  private drawnGeometries: L.FeatureGroup;
  private geometries_drawn: boolean;

  constructor(element: HTMLDivElement) {
    console.log('constructing');
    this.divElement = element;
    this.drawnGeometries = L.featureGroup();
    this.geometries_drawn = false;
  }

  setMap(map: L.Map) {
    this.map = map;
    var me = this;

    const drawControl = new L.Control.Draw({
      edit: {
        featureGroup: this.drawnGeometries,
      },
    });
    map.addControl(drawControl);

    this.drawnGeometries.clearLayers();
    map.on(L.Draw.Event.CREATED, (e: any) => {
      // or on DRAWSTOP
      this.drawnGeometries.addLayer(e.layer);
      this.geometries_drawn = true;

      console.log('LeafletClient: drawn geometry');
      me.divElement.dispatchEvent(new CustomEvent('django-leaflet-drawn'));
    });
    if (this.geometries_drawn) map.addLayer(this.drawnGeometries);
  }

  public initialize() {
    console.log('initializing');
    const me = this;
    this.divElement.addEventListener('django-leaflet-client-on-map-ready', evt => {
      const map = (evt as CustomEvent).detail.map as L.Map;
      console.log('Map: ', map);
      me.setMap(map);
    });
    this.divElement.dispatchEvent(new CustomEvent('leaflet-client-initialized', {}));
  }

  public checkValidity(): boolean {
    //TODO: bei korrektem Event feuern
    let geom_valid: boolean = true;
    //console.log('LeafletClient: check validity', this.drawnGeometries.getLayers());

    // Methode 1:
    // const features = this.drawnGeometries.toGeoJSON().features; // TODO(12.06): mit den Layern aus drawGeometries arbeiten!!!
    // if (features.length > 0) {
    //   features.forEach(feat => {
    //     //geom_valid = geom_valid && !booleanValid(g.geometry); // correct
    //     geom_valid = feat.geometry.type === 'LineString' ? false : true; // zum Testen
    //     //console.log(g.geometry, booleanValid(g.geometry)); // turf.kinks -> self intersection
    //     feat.properties.valid = geom_valid;
    //   });
    //   this.changeGeomColor();
    // }

    // Methode 2:
    this.drawnGeometries.eachLayer(layer => {
      const geometry = layer.toGeoJSON().geometry;
      geom_valid = geometry.type === 'LineString' ? false : true; // zum Testen
      // layer.feature = layer.feature || {};
      // layer.feature.properties = layer.feature.properties || {};
      // layer.feature.properties.valid = geom_valid; // -> wollen nciht, dass es danach in DB auftaucht!
      console.log('layer', this.drawnGeometries.getLayers());
      this.changeGeomColor(layer, geom_valid);
    });

    //Methode 3:
    // this.drawnGeometries.toGeoJSON().features.forEach(feature => { // does not work because of copy from toGeoJSON()
    //   const type = feature.geometry.type;
    //   geom_valid = type === 'LineString' ? false : true; // zum Testen
    //   feature.properties = feature.properties || {};
    //   feature.properties.valid = geom_valid;
    //   console.log('feature', feature);
    // });

    return geom_valid;
  }

  public getGeometry(): string | undefined {
    if (!this.map) return undefined;

    if (!this.geometries_drawn) {
      this.drawnGeometries.clearLayers();
      this.map.eachLayer(layer => {
        if (layer instanceof L.Polygon || layer instanceof L.Polyline || layer instanceof L.Marker) {
          const geom_found = this.drawnGeometries.toGeoJSON().features.find(f => JSON.stringify(f.geometry) === JSON.stringify(layer.toGeoJSON().geometry));
          // check if layer is not contained multiple times
          if (!geom_found) this.drawnGeometries.addLayer(layer);
        }
      });
    }

    const geometries = this.drawnGeometries.toGeoJSON().features.map(f => f.geometry);
    const geometryCollection = {
      type: 'GeometryCollection',
      geometries: geometries,
    };
    return JSON.stringify(geometryCollection);
  }

  public changeGeomColor(layer: Layer, is_valid: boolean) {
    // if (this.map) {
    //   this.map.removeLayer(feature);
    //   L.geoJSON(feature, {
    //     style: {
    //       color: 'red',
    //     },
    //   }).addTo(this.map);
    // TODO: remove geom from before
    //}

    // Methode 2
    //this.drawnGeometries.eachLayer(layer => {
      //console.log('layer 2', layer.toGeoJSON());
    //  const isValid = layer.feature?.properties?.valid;

      if ((layer as any).setStyle && !is_valid) {
        (layer as any).setStyle({
          color: 'red',
        });
      }
    //});
  }
}

const PN = Symbol('DjangoLeafletClientElement');

export class LeafletClientElement extends HTMLDivElement {
  private [PN]: LeafletClientField; // hides internal implementation

  constructor() {
    super();
    this[PN] = new LeafletClientField(this);
  }

  connectedCallback() {
    this[PN].initialize();
  }

  checkValidity() {
    return this[PN].checkValidity();
  }

  getGeometry() {
    return this[PN].getGeometry();
  }
}
