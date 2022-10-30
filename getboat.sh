#!/bin/sh
Q=`cat <<EOF
query MyQuery(\\$oga_no: Int! ) {
  boat(where: {oga_no: {_eq: \\$oga_no}}) {
    air_draft
    beam
    builderByBuilder {
      name
      id
    }
    callsign
    constructionMaterialByConstructionMaterial {
      name
    }
    constructionMethodByConstructionMethod {
      name
    }
    construction_details
    construction_material
    construction_method
    created_at
    designClassByDesignClass {
      name
      id
    }
    designerByDesigner {
      id
      name
    }
    draft
    fishing_number
    for_sales {
      created_at
      flexibility
      offered
      price_flexibility {
        text
      }
      reduced
      sales_text
      seller_gold_id
      seller_member
      sold
      summary
      updated_at
    }
    full_description
    genericTypeByGenericType {
      name
    }
    handicap_data
    hin
    home_country
    home_port
    hullFormByHullForm {
      name
    }
    id
    image_key
    keel_laid
    launched
    length_on_deck
    mainsail_type
    mssi
    name
    nhsr
    nsbr
    oga_no
    ownerships
    place_built
    previous_names
    reference
    rigTypeByRigType {
      name
    }
    sail_number
    sail_type {
      name
    }
    selling_status
    short_description
    sparMaterialBySparMaterial {
      name
    }
    ssr
    thumb
    uk_part1
    update_id
    updated_at
    website
    year
    year_is_approximate
  }
}
EOF`
echo $Q
curl 'https://api-oga.herokuapp.com/v1/graphql' \
--silent \
-X 'POST' \
-H 'Content-Type: application/json' \
-H 'Pragma: no-cache' \
-H 'Accept: application/json' \
-H 'Accept-Language: en-gb' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
--data-binary "{\"query\": \"$Q\",\"variables\":{\"oga_no\":$1},\"operationName\":\"MyQuery\"}" 
