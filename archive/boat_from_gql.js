const core = require('@actions/core');
const fetch = require("node-fetch");
const {Base64} = require('js-base64');
const { Octokit } = require("@octokit/action");

const octokit = new Octokit();

async function fetchGraphQL(operationsDoc, operationName, variables) {
  const result = await fetch(
    "https://api-oga.herokuapp.com/v1/graphql",
    {
      method: "POST",
      body: JSON.stringify({
        query: operationsDoc,
        variables: variables,
        operationName: operationName
      })
    }
  );
  const d = await result.json();
  return d.data.boat[0];
}

const operationsDoc = `
  query MyQuery($oga_no: Int!) {
    boat(where: {oga_no: {_eq: $oga_no}}) {
      id name previous_names year year_is_approximate place_home built_port home_country ssr
      sail_number nhsr nsbr oga_no fishing_number callsign mssi full_description image_key uk_part1
      spar_material
      rig_type construction_material construction_method construction_details
      draft
      generic_type
      handicap_data
      hull_form
      keel_laid
      launched
      length_on_deck
      mainsail_type
      short_description
      updated_at
      website
      beam
      air_draft
      reference
      ownerships
      builder designer design_class
      constructionMaterialByConstructionMaterial { name }
      constructionMethodByConstructionMethod { name }
      designClassByDesignClass { name }
      designerByDesigner { name }
      rigTypeByRigType { name }
      genericTypeByGenericType { name }
      builderByBuilder { name notes }
      for_sale_state { text }
      for_sales(limit: 1, order_by: {updated_at: desc}) {
        asking_price
        flexibility
        offered
        price_flexibility { text }
        reduced
        sales_text
        sold
        summary
        updated_at
      }
      engine_installations { engine installed removed }
    }
  }
`;

function fetchMyQuery(oga_no) {
  return fetchGraphQL(
    operationsDoc,
    "MyQuery",
    {"oga_no": oga_no}
  );
}

const template = {
  staticQueryHashes: [],
  componentChunkName: "component---src-templates-boattemplate-jsx",
  path: "/boat/$1",
  result: {
    pageContext: {
      pathSlug: "/boat/$1",
      home: "/",
      absolute: "https://oga.org.uk",
      boat: {}
    }
  }
}

function makedoc(boat) {
  const doc = {...template};
  doc.path = `/boat/${boat.oga_no}`;
  doc.result.pageContext.pathSlug = doc.path;
  doc.result.pageContext.boat = boat;
  return doc;
}

async function create_or_update_boat(repository, oga_no) {
  const path = `/page-data/boat/${oga_no}/page-data.json`;
  const url = `/repos/${repository}/contents${path}`;
  console.log('create_or_update_boat', url);
  const [owner, repo] = repository.split('/');
  const p = { owner, repo, path };
  try {
    const r = await octokit.request(`GET ${url}`);
    p.sha = r.data.sha;
    console.log('got boat from repo with sha', p.sha);
  } catch(e) {
    console.log('new boat', oga_no);
  }
  p.message = 'update from postgreSQL';
  const boat = await fetchMyQuery(oga_no);
  console.log('got boat from database');
  p.content = Base64.encode(JSON.stringify(makedoc(boat)));
  const r = await octokit.request(`PUT ${url}`, p);
  console.log('put boat from database to repo');
  return r.data.content.sha;
}

async function delete_boat(repository, oga_no) {
  const path = `/page-data/boat/${oga_no}/page-data.json`;
  const url = `/repos/${repository}/contents${path}`;
  console.log('delete_boat', url);
  const [owner, repo] = repository.split('/');
  const p = { owner, repo, path };
  try {
    const r = await octokit.request(`GET ${url}`);
    p.sha = r.data.sha;
    p.message = 'delete from postgreSQL';
    await octokit.request(`DELETE ${url}`, p);
    console.log('remove boat from repo');
    return r.data.content.sha;
  } catch(e) {
    console.log('no existing boat', oga_no);
  }
  return `nothing to do for ${oga_no}`;
}

try {
  if (core.getInput('op') === 'DELETE') {
    delete_boat(core.getInput('repo'), core.getInput('oga-no'))
    .then((data) => {
      core.setOutput("sha", data);
    })
    .catch(error => {
      console.log('handled promise error on delete_boat', error);
      core.setFailed(error.message);
    });  
  } else {
    create_or_update_boat(core.getInput('repo'), core.getInput('oga-no'))
    .then((data) => {
      core.setOutput("sha", data);
    })
    .catch(error => {
      console.log('handled promise error on create_or_update_boat', error);
      core.setFailed(error.message);
    });  
  }
} catch (error) {
  console.log(`exception in delete, create, or update boat ${core.getInput('oga-no')}`);
  core.setFailed(error.message);
}

