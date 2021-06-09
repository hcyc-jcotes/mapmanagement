import { render, screen } from '@testing-library/react';
import App from './App';
import {testLayer} from '@deck.gl/test-utils';
import {PathLayer, ScatterplotLayer } from '@deck.gl/layers';
import { HeatmapLayer, HexagonLayer} from '@deck.gl/aggregation-layers';
import TopMenu from './layouts/topMenu';
import React from 'react';
import data from './json/coordinates.json'
/*
test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
*/

test('PathLayer#tests', () => {
  testLayer({Layer: PathLayer, testCases: [
    // Test case 1
    {
      props: {
        data: [
            {
                "id": 50,
                "camera_make": "Apple",
                "captured_at": "2018-12-21 - 09:30:43",
                "key": "b8liem9mj3fh8cbbw7siuh",
                "pano": false,
                "points_in_seq": 15,
                "coordinates": [
                    [
                        138.5867161,
                        -34.9292558
                    ],
                    [
                        138.5868206,
                        -34.929255
                    ],
                    [
                        138.5868892,
                        -34.9292564
                    ],
                    [
                        138.5869559,
                        -34.9292545
                    ],
                    [
                        138.5870229,
                        -34.9292543
                    ],
                    [
                        138.5870564,
                        -34.9292516
                    ],
                    [
                        138.5870898,
                        -34.92925
                    ],
                    [
                        138.5871232,
                        -34.9292475
                    ],
                    [
                        138.5871565,
                        -34.9292505
                    ],
                    [
                        138.58719,
                        -34.9292487
                    ],
                    [
                        138.5872232,
                        -34.9292481
                    ],
                    [
                        138.5872547,
                        -34.9292397
                    ],
                    [
                        138.5872873,
                        -34.9292352
                    ],
                    [
                        138.5873199,
                        -34.9292309
                    ],
                    [
                        138.5873523,
                        -34.9292255
                    ]
                ],
                "first": [
                    138.5867161,
                    -34.9292558
                ],
                "last": [
                    138.5873523,
                    -34.9292255
                ]
            }
        ],
        getPath: (d) => d.coordinates,},
      onAfterUpdate({layer, oldState}) {
        expect(layer.state.instanceCount).toBe(oldState.instanceCount);
      }
    },
    // Test case 2
    {
      updateProps: {
        // will be merged with the previous props
        getLineWidth: 1,
      },
      onAfterUpdate({layer}) {
        expect(layer.props.getLineWidth).toBe(1);
      }
    }
  ]});
});

test('ScatterplotLayer#tests', () => {
  testLayer({Layer: ScatterplotLayer, testCases: [
    // Test case 1
    {
      props: {
        data: [
            {
                "id": 16539,
                "image_key": "cod2wusx0W4hO9QNfDWFd7",
                "sequence_key": 50,
                "direction": 89.46745418432943,
                "neighbors": "[16539, 64650, 64651, 64649, 64652, 64648, 16572, 64653, 64647]",
                "filename": "./Images/img_cod2wusx0W4hO9QNfDWFd7.jpg",
                "coordinates": [
                    138.5867161,
                    -34.9292558
                ]
            },
            {
                "id": 16540,
                "image_key": "iT8Qtr6IGHZVQ5c14SJLKF",
                "sequence_key": 50,
                "direction": 91.4195191067198,
                "neighbors": "[16540, 64651, 64650, 64652, 64649, 64653, 64648, 64654]",
                "filename": "./Images/img_iT8Qtr6IGHZVQ5c14SJLKF.jpg",
                "coordinates": [
                    138.5868206,
                    -34.929255
                ]
            }
        ],
        getPosition: (d) => d.coordinates,},
      onAfterUpdate({layer, oldState}) {
        expect(layer.state.data).toBe(oldState.data);
      }
    },
    // Test case 2
    {
      updateProps: {
        // will be merged with the previous props
        getRadius: 3,
      },
      onAfterUpdate({layer}) {
        expect(layer.props.getRadius).toBe(3);
      }
    }
  ]});
});


test('HeatmapLayer#tests', () => {
  testLayer({Layer: HeatmapLayer, testCases: [
    // Test case 1
    {
      props: {
        data: [
            {
                "id": 16539,
                "image_key": "cod2wusx0W4hO9QNfDWFd7",
                "sequence_key": 50,
                "direction": 89.46745418432943,
                "neighbors": "[16539, 64650, 64651, 64649, 64652, 64648, 16572, 64653, 64647]",
                "filename": "./Images/img_cod2wusx0W4hO9QNfDWFd7.jpg",
                "coordinates": [
                    138.5867161,
                    -34.9292558
                ]
            },
            {
                "id": 16540,
                "image_key": "iT8Qtr6IGHZVQ5c14SJLKF",
                "sequence_key": 50,
                "direction": 91.4195191067198,
                "neighbors": "[16540, 64651, 64650, 64652, 64649, 64653, 64648, 64654]",
                "filename": "./Images/img_iT8Qtr6IGHZVQ5c14SJLKF.jpg",
                "coordinates": [
                    138.5868206,
                    -34.929255
                ]
            }
        ],
      getPosition: (d) => d.coordinates,},
      onAfterUpdate({layer, oldState}) {
        expect(layer.state.data).toBe(oldState.data);
      }
    },
    // Test case 2
    {
      updateProps: {
        // will be merged with the previous props
        radiusPixels: 30,
      },
      onAfterUpdate({layer}) {
        expect(layer.props.radiusPixels).toBe(30);
      }
    }
  ]});
});


test('HexagonLayer#tests', () => {
  testLayer({Layer: HexagonLayer, testCases: [
    // Test case 1
    {
      props: {
        data: [
            {
                "id": 16539,
                "image_key": "cod2wusx0W4hO9QNfDWFd7",
                "sequence_key": 50,
                "direction": 89.46745418432943,
                "neighbors": "[16539, 64650, 64651, 64649, 64652, 64648, 16572, 64653, 64647]",
                "filename": "./Images/img_cod2wusx0W4hO9QNfDWFd7.jpg",
                "coordinates": [
                    138.5867161,
                    -34.9292558
                ]
            },
            {
                "id": 16540,
                "image_key": "iT8Qtr6IGHZVQ5c14SJLKF",
                "sequence_key": 50,
                "direction": 91.4195191067198,
                "neighbors": "[16540, 64651, 64650, 64652, 64649, 64653, 64648, 64654]",
                "filename": "./Images/img_iT8Qtr6IGHZVQ5c14SJLKF.jpg",
                "coordinates": [
                    138.5868206,
                    -34.929255
                ]
            }
        ],
      getPosition: (d) => d.coordinates,},
      onAfterUpdate({layer, oldState}) {
        expect(layer.state.data).toBe(oldState.data);
      }
    },
    // Test case 2
    {
      updateProps: {
        // will be merged with the previous props
        radius: 100,
      },
      onAfterUpdate({layer}) {
        expect(layer.props.radius).toBe(100);
      }
    }
  ]});
});

// Thanh test 1
describe('test for app', () => {
  it('renders Layers and Regions text initially', () => {
  const { getByText } = render(<TopMenu />);
  expect(getByText('Regions'));
  expect(getByText('Layers'));
  })
  })

// Thanh test 2
const image_key_of_id2 = "z9Z9bTtxZa7WeNd4RvN3YA";
const neighbor_of_id = data[0].neighbors;
test('If id2 is neighbor of id1 then the image key get from id2 in the neighbor list of id1 should be the same as original image key of id2', ()=>{
  
  expect(data[neighbor_of_id[1]].image_key).toContain(image_key_of_id2);
});