//FOR MILESTONE 1 - TEAM 03
// Sidebar for the frontend
import React, { useState, useEffect } from 'react';
import styles from 'styled-components';
import { observer } from 'mobx-react';
import axios from 'axios';
import { ScatterplotLayer } from 'deck.gl';
import { PathLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { ArcLayer } from '@deck.gl/layers';
import { HexagonLayer } from '@deck.gl/aggregation-layers';
import { DatePicker, Menu, Dropdown, Button, notification, Space, Tooltip } from 'antd';
import { ControlFilled, EnvironmentFilled, ExclamationCircleFilled } from '@ant-design/icons';
import LayerStore from '../store/layerStore';
import {nw , se, zoom} from '../App';
import LoadingStore from '../store/loadingStore';

const TopMenu = ({ handleChangeCoordinate }) => {
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [regionsresult, emptyregion] = useState([]);
    const [previousLayer, setpreviousLayer] = useState(0);
    let neweast = se[0] + 0.01;
    const [from, setfrom] = useState("")
    const [to, setto] = useState("")
    const getLineColor = () => {
      const green = Math.floor(Math.random() * 255) + 1;
      const red = Math.floor(Math.random() * 255) + 1;
      const black = Math.floor(Math.random() * 255) + 1;
      return [green, red, black];
    };

    // const getRegions = async () => {
    // await axios
    //     .get(`/api/regions`)
    //     .then((response) => {
    //         emptyregion(response.data);
    //     })
    //     .catch((error) => {
    //     console.log('Error', error);
    //     });
    // };

    // useEffect(() => {
    // getRegions();
    // }, []);

    
  //GET REGIONS
  useEffect(() => {
    fetch('/api/regions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((resp) => resp.json())
      .then((resp) => emptyregion(resp));
  }, []);



    //HANDLE THE CHANGE OF LAYERS
    const handleOnChange = async(e,currentfrom,currentto,validator) => {
        LoadingStore.setLoadingProcess(true);
        let value = previousLayer;
        let selectedfrom = from;
        let selectedto = to;
        if(e.key){
           value = parseInt(e.key);
           setpreviousLayer(value);
		}
        if(validator){
            selectedfrom = currentfrom;
            selectedto = currentto;
		}
        LayerStore.removeAllLayers();
        let url = '';
        if(selectedfrom.length  == 0){
            url = `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}`;
		}
        else{
            url = `?min_lon=${nw[0]}&max_lon=${neweast}&min_lat=${se[1]}&max_lat=${nw[1]}&from=${selectedfrom}&to=${selectedto}`;
		}
        switch (value) {
          case 0:
            LoadingStore.setLoadingProcess(false);
             return LayerStore.removeAllLayers();
          case 1:
            if(zoom >= 15){
              const dataAdelaide = await axios
              .get(`/api/coordinates/` + url)
              .then((response) => {
                //LoadingStore.setLoadingProcess(false);
                return response.data;
              })
              .catch((e) => {
                LoadingStore.setLoadingProcess(false);
                alert('Cannot set layer', e);
              });
    
            const dataGeojson = await axios
              .get(`/api/sequences/` + url)
              .then((response) => {
                 LoadingStore.setLoadingProcess(false);
                return response.data;
              })
              .catch((e) => {
                LoadingStore.setLoadingProcess(false);
                alert('Cannot set layer', e);
              });
                const scatterLayer = new ScatterplotLayer({
                    id: 'adelaide-points',
                    data: dataAdelaide,
                    pickable: true,
                    filled: true,
                    getPosition: (d) => d.coordinates,
                    getRadius: (d) => 2,
                    getFillColor: [255, 200, 0],
                });
                const geoLayer = await new PathLayer({
                    id: 'geojson-layer',
                    data: dataGeojson,
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
                LayerStore.setLayerMap(geoLayer);            
                return LayerStore.setLayerMap(scatterLayer);
            } else{
              // LoadingStore.setLoadingProcess(false);
                notification.open({
                    message: 'Showing sequences only.',
                    description:
                      'Zoom in to see the points in the map.',
                    icon: <ExclamationCircleFilled style={{ color: '#ffec3d' }} />,
                });

                const data_Geojson = await axios
                .get(`/api/sequences/` + url)
                .then((response) => {
                  LoadingStore.setLoadingProcess(false);
                  return response.data;
                })
                .catch((e) => {
                  LoadingStore.setLoadingProcess(false);
                  alert('Cannot set layer', e);
                });

                const geoLayer = new PathLayer({
                    id: 'geojson-layer',
                    data: data_Geojson,
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
			}            
          case 2:
            if(zoom >= 14){
              const dataHeatmaplayer = await axios
              .get(`/api/coordinates/` + url)
              .then((response) => {
                LoadingStore.setLoadingProcess(false);
                return response.data;
              })
              .catch((e) => {
                LoadingStore.setLoadingProcess(false);
                alert('Cannot set layer', e);
              });
                const heatmaplayer = new HeatmapLayer({
                  id: 'heatmap-layer',
                  data:  dataHeatmaplayer,                 
                  pickable: true,
                  filled: true,
                  getPosition: (d) => d.coordinates,
                  getRadius: (d) => 3,
                  radiusPixels: 30,
                  intensity: 1,
                  threshold: 0.05,
                });
                return LayerStore.setLayerMap(heatmaplayer);
            }else{
                LoadingStore.setLoadingProcess(false);
                notification.open({
                    message: 'Not displaying layer',
                    description:
                      'Zoom in to see the Sequence Distribution Layer.',
                    icon: <ExclamationCircleFilled style={{ color: '#ffec3d' }} />,
                });
                return LayerStore;     
			}
          case 3:
            if(zoom >= 14){
              const dataHexagonlayer = await axios
              .get(`/api/coordinates/` + url)
              .then((response) => {
                LoadingStore.setLoadingProcess(false);
                return response.data;
              })
              .catch((e) => {
                LoadingStore.setLoadingProcess(false);
                alert('Cannot set layer', e);
              });
                const hexagonlayer = await new HexagonLayer({
                  id: 'hexagon-layer',
                  data: dataHexagonlayer,
                  pickable: true,
                  extruded: true,
                  radius: 100,
                  elevationScale: 4,
                  getPosition: (d) => d.coordinates,
                });
                return LayerStore.setLayerMap(hexagonlayer);
            }else{
                LoadingStore.setLoadingProcess(false);
                notification.open({
                    message: 'Not displaying layer',
                    description:
                      'Zoom in to see the Location Distribution Layer.',
                    icon: <ExclamationCircleFilled style={{ color: '#ffec3d' }} />,
                });
                return LayerStore;     
			}
          default:
            return LayerStore.removeAllLayers();
        }
    };

    //LAYERS MENU
    const layers = (
      <Menu onClick={handleOnChange} selectable={true} defaultSelectedKeys={['0']}>
        <Menu.Item key="0">
          No Layer
        </Menu.Item>
        <Menu.Item key="1">
          Location and Sequences
        </Menu.Item>
        <Menu.Item key="2">
          Sequence Distribution
        </Menu.Item>
        <Menu.Item key="3">
          Location Distribution
        </Menu.Item>
      </Menu>
    );

    //HANDLES THE CHANGES OF REGIONS
    const handleOnChangeRegions = (selectedValue) => {
        const selected_lat = selectedValue.item.props.lat;
        const selected_lon = selectedValue.item.props.lon;
        nw[0] = selected_lon - 0.028;
        se[0] = selected_lon + 0.028;
        neweast = se[0] - 0.0379;
        se[1] = selected_lat - 0.0283; 
        nw[1] = selected_lat + 0.0289;
        handleChangeCoordinate(selected_lon, selected_lat);
    };

    //REGIONS MENU
    const regions = (
      <Menu onClick={handleOnChangeRegions} selectable={true} defaultSelectedKeys={['1']}>
      {
        regionsresult
            .sort((a, b) => a.name > b.name ? 1 : -1)
            .map(x=>{
            return(
                <Menu.Item key={x.id} lat={x.view_latitude} lon={x.view_longitude}>
                    {x.name}
                </Menu.Item>
			)})       
	  }
      </Menu>
    );
    
    //HANDLES THE CHANGES OF DATES
    const handleChangeDebut = (range,dateStrings) => {
        const currentfrom = dateStrings[0];
        const currentto = dateStrings[1];
        setfrom(dateStrings[0]);
        setto(dateStrings[1]);
        console.log("currentfrom",currentfrom);
        if(currentfrom){
            handleOnChange(0,currentfrom,currentto,true);
		}else{
            handleOnChange(0,"","",true);
        }
        
    };

    const { RangePicker } = DatePicker;

    //SET THE TOP MENU
    return (
        <Layout>
            <RangePicker onChange={handleChangeDebut}/>     
            <Dropdown.Button 
                overlay={layers} 
                //trigger={['click']}
                placement="bottomCenter" 
                icon={<ControlFilled />}
            >
            Layers
            </Dropdown.Button>        
            <Dropdown.Button 
                overlay={regions} 
                //trigger={['click']}
                placement="bottomCenter" 
                icon={<EnvironmentFilled />}
            >
            Regions
            </Dropdown.Button>        
        </Layout>
    );
};

export default observer(TopMenu);

const Layout = styles.div`
  padding: 10px;
  background-color: transparent;
  color: white;
  position: relative;
  z-index: 99;
  display: flex;
  transition: width 250ms ease 0s;
  border-radius: 5px;
  `;










