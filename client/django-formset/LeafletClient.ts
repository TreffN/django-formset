import booleanValid from '@turf/boolean-valid';
import { Layer } from 'leaflet';

class LeafletClientField {
  private readonly divElement: HTMLDivElement;
  private map: L.Map | undefined;
  private drawnGeometries: L.FeatureGroup;
  private geometries_drawn: boolean;

  constructor(element: HTMLDivElement) {
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
    const me = this;
    this.divElement.addEventListener('django-leaflet-client-on-map-ready', evt => {
      const map = (evt as CustomEvent).detail.map as L.Map;
      me.setMap(map);
    });
    this.divElement.dispatchEvent(new CustomEvent('leaflet-client-initialized', {}));
  }

  public checkValidity(): boolean { //TODO: timed correctly? 
    let geom_valid: boolean = true;
 
    this.drawnGeometries.eachLayer(layer => {
      const geometry = layer.toGeoJSON().geometry;
      geom_valid = geom_valid && booleanValid(geometry);
      this.changeGeomColor(layer, geom_valid);
    });

    return geom_valid;
  }

  public getPolygonCollection(): string | undefined {
    if (!this.map) return undefined;

    if (!this.geometries_drawn) {
      this.drawnGeometries.clearLayers();
      this.map.eachLayer(layer => {
        if (layer instanceof L.Polygon || layer instanceof L.Polyline || layer instanceof L.Marker) {
          // check if layer is not contained multiple times
          const geom_found = Array.from(this.drawnGeometries.toGeoJSON().features).find(f => JSON.stringify(f.geometry) === JSON.stringify(layer.toGeoJSON().geometry));
          if (!geom_found) this.drawnGeometries.addLayer(layer);
        }
      });
    }

    const polygonFeature = this.drawnGeometries.toGeoJSON().features.findLast(f => (f.geometry?.geometry?.type ?? f.geometry?.type) === 'Polygon');

    if (!polygonFeature) {
      return undefined;
    }
    
    const polygonCollection = {
      type: polygonFeature.geometry?.geometry?.type ?? polygonFeature.geometry?.type,
      coordinates: polygonFeature.geometry?.geometry?.coordinates ?? polygonFeature.geometry?.coordinates,
    };
    return JSON.stringify(polygonCollection);
  }

  public changeGeomColor(layer: Layer, is_valid: boolean) {
      if ((layer as any).setStyle && !is_valid) {
        (layer as any).setStyle({
          color: 'red',
        });
      }
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

  getPolygonCollection() {
    return this[PN].getPolygonCollection();
  }
}
