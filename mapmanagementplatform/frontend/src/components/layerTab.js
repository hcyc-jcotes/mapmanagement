import 'react-datepicker/dist/react-datepicker.css';
import React, { useState } from 'react';
import styles from 'styled-components';
import LayerStore from '../store/layerStore';
import { observer } from 'mobx-react';
import DatePicker from 'react-datepicker';

import moment from 'moment';

import { ScatterplotLayer } from 'deck.gl';
import { PathLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { ArcLayer } from '@deck.gl/layers';
import { HexagonLayer } from '@deck.gl/aggregation-layers';

const getLineColor = () => {
  const green = Math.floor(Math.random() * 255) + 1;
  const red = Math.floor(Math.random() * 255) + 1;
  const black = Math.floor(Math.random() * 255) + 1;
  return [green, red, black];
};

const LayerTab = () => {
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const nw = [138.54791279964593, -34.90016403691384];
  const se = [138.65357936554115, -34.954408297248236];
  const neweast = se[0] + 0.01;

  const handleOnChange = (e) => {
    const value = parseInt(e.target.value);
    switch (value) {
      case 0:
        const scatterLayer = new ScatterplotLayer({
          id: 'adelaide-points',
          data:
            `/api/coordinates/` +
            `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}`,
          pickable: true,
          filled: true,
          getPosition: (d) => d.coordinates,
          getRadius: (d) => 3,
          getFillColor: [255, 200, 0],
        });
        return LayerStore.setLayerMap(scatterLayer);
      case 1:
        const geoLayer = new PathLayer({
          id: 'geojson-layer',
          data:
            `/api/sequences/` +
            `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}`,
          pickable: true,
          stroked: false,
          filled: true,
          extruded: true,
          getPath: (d) => d.coordinates,
          lineWidthScale: 10,
          lineWidthMinPixels: 10,
          getColor: [255, 200, 0],
          getLineColor,
          getRadius: 100,
          getLineWidth: 1,
          getElevation: 30,
        });
        return LayerStore.setLayerMap(geoLayer);
      case 2:
        const heatmaplayer = new HeatmapLayer({
          id: 'heatmap-layer',
          data:
            `/api/coordinates/` +
            `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}`,
          pickable: true,
          filled: true,
          getPosition: (d) => d.coordinates,
          getRadius: (d) => 3,
          radiusPixels: 30,
          intensity: 1,
          threshold: 0.05,
        });
        return LayerStore.setLayerMap(heatmaplayer);
      case 3:
        const hexagonlayer = new HexagonLayer({
          id: 'hexagon-layer',
          data:
            `/api/coordinates/` +
            `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}`,
          pickable: true,
          extruded: true,
          radius: 200,
          elevationScale: 4,
          getPosition: (d) => d.coordinates,
        });
        return LayerStore.setLayerMap(hexagonlayer);
      default:
        return LayerStore.setLayerMap({});
    }
  };

  const getData = () => {
    const sequenceTime = new PathLayer({
      id: 'sequenceTime-layer',
      data: `api/sequences/?from=${moment(startDate).format('YYYY-MM-DD')}&to=${moment(
        endDate
      ).format('YYYY-MM-DD')}`,
      pickable: true,
      stroked: false,
      filled: true,
      extruded: true,
      getPath: (d) => d.coordinates,
      lineWidthScale: 10,
      lineWidthMinPixels: 10,
      getColor: [109, 123, 247],
      getLineColor: [3, 28, 252],
      getRadius: 100,
      getLineWidth: 1,
      getElevation: 30,
    });
    LayerStore.setLayerMap(sequenceTime);
  };
  return (
    <Container>
      <Header>
        <Title>Layers</Title>
        From:
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
          maxDate={endDate}
          dateFormat="yyyy-MMMM-dd"
          closeOnScroll={true}
        />
        <br />
        To:
        <DatePicker
          selected={endDate}
          onChange={(date) => setEndDate(date)}
          minDate={startDate}
          dateFormat="yyyy-MMMM-dd"
          closeOnScroll={true}
        />
        <br />
        <BtnGetData onClick={() => getData()}>{`Get sequences data From: ${moment(startDate).format(
          'YYYY-MM-DD'
        )} --- To:${moment(endDate).format('YYYY-MM-DD')}`}</BtnGetData>
        <BtnGetData onClick={() => LayerStore.removeLayer('sequenceTime-layer')}>
          Remove sequences data line
        </BtnGetData>
      </Header>
      <Body>
        <form>
          <CheckboxButton>
            <input type="checkbox" name="layer" value={0} onChange={handleOnChange} />
            <p>Scatter Plot Layer</p>
          </CheckboxButton>
          <CheckboxButton>
            <input type="checkbox" name="layer" value={1} onChange={handleOnChange} />
            <p>Path Layer</p>
          </CheckboxButton>
          <CheckboxButton>
            <input type="checkbox" name="layer" value={2} onChange={handleOnChange} />
            <p>HeatMap Layer</p>
          </CheckboxButton>
          <CheckboxButton>
            <input type="checkbox" name="layer" value={3} onChange={handleOnChange} />
            <p>Hexagon Layer</p>
          </CheckboxButton>
        </form>
      </Body>
    </Container>
  );
};

export default observer(LayerTab);

const Container = styles.div`
  padding: 16px;
  height: 100%;
  background-color: transparent;
  color: white;
  border-radius: 5px;
`;

const Header = styles.div`
  border-bottom: 0.5px solid lightgrey;
  padding-bottom: 16px;
`;

const BtnGetData = styles.button`
  align-items: center;
  background-color: rgb(106, 116, 133);
  border-radius: 10px;
  color: white;
  cursor: pointer;
  justify-content: center;
  font-size: 14px;
  line-height: 19px;
  outline: none;
  padding: 6px 10px;
  text-align: center;
  margin-top: 16px;
  border: none;
`;

const Title = styles.h1`
margin-bottom: 16px;
`;

const Body = styles.div`
  padding-top: 16px;
`;

const CheckboxButton = styles.div`
  display: flex;
  align-items: center;
  & > p {
    margin-left: 5px;
  }
`;
