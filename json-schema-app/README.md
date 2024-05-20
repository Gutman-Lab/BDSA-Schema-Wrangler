# JSON Schema Viewer
View the BDSA JSON schema.

## Instructions
### Generating required files
* Navigate into "json-schema-app" directory (e.g. ```$ cd bdsa-schema-json```)
* Create required files: ```$ 

To run when simply viewing, use the following commands:
1. ```$ docker build -t bdsa-json-viewer .```
2. ```$ docker run -it --rm -p8050:8050 bdsa-json-viewer```
    - Runs on localhost port 8050

When running to develop the application further / make changes run with the following after building.

2. ```$ docker run -it --rm -p8050:8050 -v $(pwd):/app bdsa-json-viewer```

To update the JSON schema html files run this: ```$ generate-schema-doc bdsa-schema.json assets/```