# Render Instructies & Credits

## Volgorde scripts

1. `render_mask_automation.py` uitvoeren in Blender bij Scripting
   - `create_scene_vineyard.py` wordt hier aangeroepen om de virtuele wijngaard op te bouwen
   - cameraplatform navigeert autonoom tussen de druivenranken met automatische render en mask generatie
   - renders komen in de `renders` map terecht
   - assets worden niet meegegeven, zie onderstaande links

2. `process_segmentation_masks.py`
   - verwerkt de maskers op pixelniveau om enkel de uniforme klassewaarden over te houden (*thresholding*)
   - validatie met `validate_masks_test.py`

3. `train_val_test_split.py` splitst de renders op in *train*, *val* en *test* datasets

## Assets mapstructuur

Zelf aan te maken en op te vullen:

- `synth-data/assets/`
  - `ground/`
  - `hdri/`
  - `vitis_vinifera/`

## Pauze bij renderen

- paar HDRI's in map `assets/hdri`
- `render_mask_automation.py` uitvoeren in Blender
- gebruikte HDRI's weghalen en nieuwe plaatsen in map
- counters manueel bijwerken in `render_mask_automation.py`
- verder renderen
- bij afloop alle HDRI's terug in map plaatsen

## Assets Links

### Ground

- [Leafy Grass2](https://freepbr.com/product/leafy-grass2/)

### HDRI

- [Drackenstein Quarry](https://polyhaven.com/a/drackenstein_quarry)
- [Evening Meadow](https://polyhaven.com/a/evening_meadow)
- [Lilienstein](https://polyhaven.com/a/lilienstein)
- [Meadow 2](https://polyhaven.com/a/meadow_2)
- [Noon Grass](https://polyhaven.com/a/noon_grass)
- [Pretoria Gardens](https://polyhaven.com/a/pretoria_gardens)

### Models

- [3D Vitis Vinifera Grape](https://www.turbosquid.com/3d-models/3d-vitis-vinifera-grape-1933790)
