# sxf-tools
SXF geospatial format tools

Parse *.RSC file

    python src/parse_rsc.py examples/100t98g.rsc

    python src/parse_rsc.py --output-objects objects.yaml --output-semantics semantics.yaml -- examples/100t98g.rsc

Parse *.SXF file

    python src/convert.py --rsc examples/100t98g.rsc examples/M-34-012.sxf
