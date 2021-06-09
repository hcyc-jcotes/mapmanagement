

import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, PathLayer } from 'deck.gl';
import axios from 'axios';
import debounce from 'debounce';
import { StaticMap } from 'react-map-gl';
import TopMenu from './layouts/topMenu';
import { WebMercatorViewport } from '@deck.gl/core';
import 'mapbox-gl/dist/mapbox-gl.css';
import styles, {keyframes} from 'styled-components';
import { observer } from 'mobx-react';
import LayerStore from './store/layerStore';
import LoadingStore from './store/loadingStore';
import './App.css';
import './index.css';
import 'antd/dist/antd.css';

// Set your mapbox access token here
const MAPBOX_ACCESS_TOKEN =
  'pk.eyJ1IjoiamNvdGVzIiwiYSI6ImNrbHpjdW5mczBoOWgycHA0OXhpN2h4ZzcifQ.xLeHcllLSZx1vijoiv2Veg';

export let zoom = 16;
export let nw = [138.54791279964593, -34.90016403691384];
export let se = [138.65357936554115, -34.954408297248236];

// Viewport settings
const INITIAL_VIEW_STATE = {
  longitude: 138.58502384357632,
  latitude: -34.93633086199087,
  zoom: 16,
  pitch: 45,
  bearing: 0,
};

function App() {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [isShowImage, setIsShowImage] = useState(false);
  const [neighbor, setNeighbor] = useState([]);
  const [indexNeighbor, setIndexNeighbor] = useState(0);
  const [currentImage, setCurrentImage] = useState({ top: 0, left: 0, object: {} }); // Moi them vao
  const [imageSlide, setImageSlide] = useState({ top: 0, left: 0, object: {} });

  const handleChangeCoordinate = (longitude, latitude) => {
    setViewState({
      ...viewState,
      longitude: parseFloat(longitude),
      latitude: parseFloat(latitude),
    });
  };

  const getApi = async (id) => {
    return await axios
      .get(`api/coordinates/?ids=${id}`)
      .then((response) => {
        return response.data[0];
      })
      .catch((error) => {
        console.log('Error', error);
      });
  };

  const setImageNeighbor = debounce(async (index) => {
    const currentPoint = await getApi(neighbor[index]);
    console.log('setImageNeighbor ~ currentPoint', currentPoint);
    if (currentPoint) {
      setImageSlide({ top: 0, left: 0, object: currentPoint });
      LayerStore.setLayerNeighborPoint(currentPoint);
    } else {
      setImageSlide({
        top: 0,
        left: 0,
        object: { image_key: 'No available data in neighbor image ' + index },
      });
    }
    if (index < neighbor.length) {
      setIndexNeighbor(index);
    }
  }, 300);

  function getTooltip({ object }) {
    if (!object) {
      return null;
    }
    //HEXAGON TOOLTIP
    if (object.position) {
      const lat = object.position[1];
      const lng = object.position[0];
      const count = object.points.length;
      return `\
        Location Distribution Information
        Latitude: ${Number.isFinite(lat) ? lat.toFixed(6) : ''}
        Longitude: ${Number.isFinite(lng) ? lng.toFixed(6) : ''}
        ${count} points in location.`;
    } else {
      //SEQUENCE TOOLTIP
      if (object.camera_make) {
        const id = object.id;
        const key = object.key;
        const captured_at = object.captured_at;
        const camera_make = object.camera_make;
        const points = object.points_in_seq;
        return `\
            Sequence Information
            ID: ${id}
            Sequence key: ${key}
            Captured at: ${captured_at}
            Camera make: ${camera_make}
            ${points} points in sequence.`;
      } else {
        //COORDINATES TOOLTIP
        if (object.image_key) {
          const id = object.id;
          const key = object.image_key;
          const lat = object.coordinates[1];
          const lng = object.coordinates[0];
          const direction = object.direction;
          const sequence_id = object.sequence_key;
          return `\
                Location Information
                ID: ${id}      
                Image Key: ${key}
                Latitude: ${Number.isFinite(lat) ? lat.toFixed(6) : ''}
                Longitude: ${Number.isFinite(lng) ? lng.toFixed(6) : ''}
                Direction: ${Number.isFinite(direction) ? lng.toFixed(2) : ''}                
                Sequence ID: ${sequence_id}.`;
        } else {
          //ANY OTHER CASE
          return null;
        }
      }
    }
  }

  return (
    <>
      <Container>
        <TopMenu handleChangeCoordinate={handleChangeCoordinate} handleChangeLayer />
        <DeckGL
          initialViewState={viewState}
          controller={true}
          layers={[...LayerStore.layerSelected]}
          redraw={true}
          onViewStateChange={({ viewState }) => {
            const viewport = new WebMercatorViewport(viewState);
            nw = viewport.unproject([0, 0]);
            se = viewport.unproject([viewport.width, viewport.height]);
            zoom = viewState.zoom;
          }}
          getTooltip={getTooltip} //           Coordinates: ${object.coordinates[0]} , ${object.coordinates[0]}
          //Direction: ${object.direction}
          //ID: ${object.id} captured at: ${captured_at}
          onClick={(props) => {
            const { x, y, object } = props;
            LayerStore.removeLayer('neighbor-points');
            if (object) {
              console.log('App ~ object', object);
              setNeighbor(JSON.parse(object.neighbors));
              setIsShowImage(true);
              setImageSlide({ top: y, left: x, object });
              setCurrentImage({ top: y, left: x, object });
              setIndexNeighbor(0);
              // Hiển thị theo sequence_ids
              const sequenceIds = new ScatterplotLayer({
                id: 'sequenceIds-layer',
                data: `/api/coordinates/?sequence_ids=${object.sequence_key}`,
                pickable: true,
                filled: true,
                getPosition: (d) => d.coordinates,
                getRadius: (d) => 3,
                getFillColor: [58, 235, 52],
              });
              const currentPath = new PathLayer({
                id: 'currentPath-layer',
                data: `/api/sequences/?ids=${object.sequence_key}`,
                pickable: true,
                stroked: false,
                filled: true,
                extruded: true,
                getPath: (d) => d.coordinates,
                lineWidthScale: 10,
                lineWidthMinPixels: 10,
                getColor: [58, 235, 52],
                getRadius: 100,
                getLineWidth: 1,
                getElevation: 40,
              });
              LayerStore.setLayerMap(currentPath);
              LayerStore.setLayerMap(sequenceIds);
              const currentObject = new ScatterplotLayer({
                id: 'currentObject-layer',
                data: [object],
                pickable: true,
                filled: true,
                getPosition: (d) => d.coordinates,
                getRadius: (d) => 3,
                getFillColor: [255, 0, 0],
              });
              LayerStore.setLayerMap(currentObject);
            } else {
              LayerStore.removeLayer('sequenceIds-layer');
              LayerStore.removeLayer('currentObject-layer');
              LayerStore.removeLayer('currentPath-layer');
              setNeighbor([]);
              setIsShowImage(false);
              setIsShowImage(false);
              setImageSlide({ top: 0, left: 0, object: {} });
              setCurrentImage({ top: 0, left: 0, object: {} });
            }
          }}
        >
          <StaticMap mapboxApiAccessToken={MAPBOX_ACCESS_TOKEN} />
        </DeckGL>
        {isShowImage && (
          <>
            <ContainerImage>
              <PrevButton
                onClick={() => setImageNeighbor(indexNeighbor - 1)}
                disabled={indexNeighbor === 0}
              >
                {'<<'}
              </PrevButton>
              <NextButton
                onClick={() => setImageNeighbor(indexNeighbor + 1)}
                disabled={indexNeighbor === neighbor.length - 1}
              >
                {'>>'}
              </NextButton>
              <Image
                src={`/static/Images/img_${imageSlide.object.image_key}.jpg`}
                alt={imageSlide.object.image_key}
                role="button"
                onClick={() => setIsShowImage(false)}
              />
            </ContainerImage>
          </>
        )}
      </Container>
      {LoadingStore.IsLoading && (
          <LoadingContainer>
            <Loading />
          </LoadingContainer>
        )}
       </>
  );
}
export default observer(App);

const Container = styles.div`
  height: 100vh;
`;

const ContainerImage = styles.div`
  width: 300px;
  height: 250px;
  position: fixed;
  bottom: 10px;
  right: 10px;
  background: gray;
  border: 1px solid;
  border-radius: 10px;
  overflow: hidden;
`;

const ButtonImage = styles.button`
  position: absolute;
  height: 250px;
  width: 25px;
  text-align: center;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  &:disabled {
    color: white;
  }
  &:hover {
    background-color: lightblue;
    color: blue;
  }
`;

const NextButton = styles(ButtonImage)`
  right: 0;
`;

const PrevButton = styles(ButtonImage)`
  left: 0;
`;

const Image = styles.img`
  position: absolute;
  width: 250px;
  height: 250px;
  top: 0;
  left: 25px;
  background: white;
`;

const CurrentImage = styles.img`   
  position: fixed;
  width: 200px;
  height: 200px;
  background: white;
  border: 1px solid;
  border-radius: 10px;
  overflow: hidden;
`;



const LoadingContainer = styles.div`
  width: 100vw;
  height: 100vh;
  position: fixed;
  z-index: 999;
  background: rgba(0,0,0,0.1);
  top: 0;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const rotate = keyframes`
  0% {
    transform: rotate(0deg); 
  }
  100% { 
    transform: rotate(360deg);
  }
`;

const Loading = styles.div`
  border: 16px solid #f3f3f3;
  border-radius: 50%;
  border-top: 16px solid #3498db;
  width: 120px;
  height: 120px;
  -webkit-animation: ${rotate} 2s linear infinite; /* Safari */
  animation: ${rotate} 2s linear infinite;
`;









