//FOR MILESTONE 1 - TEAM 03
// Displayes the layers

import { makeAutoObservable } from 'mobx';
import { ScatterplotLayer } from 'deck.gl';
// import { PathLayer } from '@deck.gl/layers';
// import { PolygonLayer } from '@deck.gl/layers';
// import { HeatmapLayer } from '@deck.gl/aggregation-layers';
// import { ArcLayer } from '@deck.gl/layers';
// import { HexagonLayer } from '@deck.gl/aggregation-layers';

// const getLineColor = () => {
//   const green = Math.floor(Math.random() * 255) + 1;
//   const red = Math.floor(Math.random() * 255) + 1;
//   const black = Math.floor(Math.random() * 255) + 1;
//   return [green, red, black];
// };

class LayerStore {
  layerSelected = [];
  constructor() {
    makeAutoObservable(this);
  }

  setLayerMap(layer) {
    const indexLayer = this.layerSelected.findIndex((item) => item.id === layer.id);
    if (indexLayer > -1) {
      if (
        layer.id === 'neighbor-points' ||
        layer.id === 'sequenceTime-layer' ||
        layer.id === 'sequenceIds-layer' ||
        layer.id === 'currentObject-layer' ||
        layer.id === 'currentPath-layer' 
      ) {
        this.layerSelected.splice(indexLayer, 1, layer);
      } else {
        this.layerSelected.splice(indexLayer, 1);
      }
    } else {
      this.layerSelected.push(layer);
    }
  }

 setLayerNeighborPoint(object) {
    const objectSelected = new ScatterplotLayer({
      id: 'neighbor-points',
      data: [object],
      pickable: true,
      filled: true,
      getPosition: (d) => d.coordinates,
      getRadius: (d) => 3,
      getFillColor: [255, 20, 147],
    });
    this.setLayerMap(objectSelected);
  }

  removeLayer(idLayer) {
    const indexLayer = this.layerSelected.findIndex((item) => item.id === idLayer);
    if (indexLayer > -1) {
      this.layerSelected.splice(indexLayer, 1);
    }
  }

  removeAllLayers() {
     this.layerSelected = [];
  }
}

const layerStore = new LayerStore();

export default layerStore;
