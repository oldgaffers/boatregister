#!/bin/sh
Q='query MyQuery($oga_no: Int!) {boat(where: {oga_no: {_eq: $oga_no}}) { id name previous_names year year_is_approximate place_built home_port home_country ssr sail_number nhsr nsbr oga_no fishing_number callsign mssi full_description image_key uk_part1 spar_material rig_type construction_material construction_method construction_details draft generic_type handicap_data hull_form keel_laid launched length_on_deck mainsail_type short_description updated_at website beam air_draft reference builder designer design_class constructionMaterialByConstructionMaterial { name } constructionMethodByConstructionMethod { name } designClassByDesignClass {name} designerByDesigner{name} rigTypeByRigType{ name } genericTypeByGenericType{name} builderByBuilder{name} for_sale_state{text} for_sales{asking_price} engine_installations{engine installed removed} }}'
curl 'https://api-oga.herokuapp.com/v1/graphql' \
--silent \
-X 'POST' \
-H 'Content-Type: application/json' \
-H 'Pragma: no-cache' \
-H 'Accept: application/json' \
-H 'Accept-Language: en-gb' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
--data-binary "{\"query\": \"$Q\",\"variables\":{\"oga_no\":$1},\"operationName\":\"MyQuery\"}"  | jq -c '.data.boat[0]' > $1.json
cat > $1 <<EOF
{
  "staticQueryHashes": [],
  "componentChunkName": "component---src-templates-boattemplate-jsx",
  "path": "/boat/$1",
  "result": {
    "pageContext": {
      "pathSlug": "/boat/$1",
      "home": "/",
      "absolute": "https://oga.org.uk",
      "boat": `cat $1.json`
    }
  }
}
EOF
jq --unbuffered -cM . $1
rm $1.json $1
