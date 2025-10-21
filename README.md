# pleiades_lpf: Linked Places Format (LPF) tools for Pleiades

`pleiades_lpf` is written by [Tom Elliott](https://isaw.nyu.edu/people/staff/tom-elliott) for the [Pleiades gazetteer of ancient places](https://pleiades.stoa.org), a project and publication of the [Institute for the Study of the Ancient World](https://isaw.nyu.edu) at New York University. 

## Roadmap 

At present, still a long way to go on fleshing out the gazetteer model. Tests pass for what is implemented; I am using a JSON LPF file from the [World Historical Gazetteer](https://whgazetteer.org/) for testing file loading.

### Classes

- [ ] Geometry
    - [x] Stub the class (in geometry.py)
    - [ ] `asdict` function
    - [ ] other functionality and data (this is largely untouched as of yet)

- [ ] Feature
    - [x] Stub the class (in geometry.py)
    - [x] Static attribute `type`="Feature" 
    - [x] `asdict` function
    - [x] `properties` attribute (dictionary)
        - [x] Validation of the `properties` attribute and its contents
        - [ ] methods for adding/getting parts of the `properties` attribute (implement as needed)
    - [x] `geometry` attribute

- [ ] FeatureCollection
    - [x] Stub the class (in geometry.py)
    - [x] Static attribute `type`="FeatureCollection" 
    - [x] Attribute `features`: `list`
    - [x] Attribute `context`: `str`
    - [ ] Attribute validation?
    - [ ] `asdict` functions

- [ ] identify and stub other classes following GeoJSON and LPF specifications.

### package-level functions

- [ ] load
    - [x] wrap `json` function from standard library
    - [x] return `FeatureCollection` instead of `dict`
- [ ] loads
    - [x] wrap `json` function from standard library
    - [ ] return `FeatureCollection` instead of `dict`
- [ ] dump
    - [x] wrap `json` function from standard library
    - [ ] expect `FeatureCollection` instead of `dict`
- [ ] dumps
    - [x] wrap `json` function from standard library
    - [ ] expect `FeatureCollection` instead of `dict`

## References

- [The Linked Places format (LPF)](https://github.com/LinkedPasts/linked-places-format?tab=readme-ov-file)
- [Python Standard Library 3.14 JSON](https://github.com/python/cpython/blob/3.14/Lib/json/__init__.py)
- [RFC 7946 The GeoJSON Format](https://datatracker.ietf.org/doc/html/rfc7946)
