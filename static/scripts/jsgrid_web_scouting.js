/* Date: MArch 12, 2020

Dev: franco@systemagency.com

This piece of software will contain many of the routines need it by
the whole internal site for System Agency (botsactions.systemagency.com)

If some issue detected, plese report it to the Developer.
*/

// var domain = "http://0.0.0.0:5000/";
var domain = "http://127.0.0.1:8000/";

function editParams(domain, endPoint, filter){

    let params = "";
    let goTo = "";

    for(var key in filter){
        item = filter[key]
        if (item != "")  params += `${key}=${item}&`
    }
    params = params.slice(0,-1);
    goTo = domain + endPoint + params;

    return {
        "goTo": goTo,
        "filter": filter
    };
}

function editParamsQuery(domain, endPoint, main_args, filter){
    /*
    param domain: str, Domain of the website.

    param endPoint: str, Endpoint to allow interactions into the backend.

    param filter: dict, Set of Key & Values to query, those values will not be
        compared using the '=' operator, becuase are not fully complete
        values.

    param main_args: dict, Set of Key & Values that will be compared using
        '=' beacause are need it for a better performance into the query.

    The order into the dictionaries it is a target. The 'main_args' dict.
        need to compose the first part of the entire dict.
    */

    let params = "";
    let goTo = "";
    let args = Object.assign({}, main_args, filter);

    for(var key in args){
        item = args[key]
        if (item != "")  params += `${key}=${item}&`
    }

    params = params.slice(0, -1);
    
    goTo = domain + endPoint + params;

    return {
        "goTo": goTo,
        "filter": filter
    };
}

async function getCountries_auth(selectorOfTheGrid, country, gsi){

    var endPoint = "queryItems";
    var staticRoute = "".concat(domain, endPoint, "?",
        "gsidataportion=", String(gsi), "&", 
        "country=", String(country)
    );

    const response = await fetch(staticRoute);
    var staticData = await response.json();

    $(selectorOfTheGrid).jsGrid({    
        
        controller: {
            
            loadData : (filter) => {
                // filter, dictionary with params    

                endPoint = "queryItems?";
                main_args = {
                    'gsidataportion' : gsi,
                    'country' : country
                };
                
                _args = editParamsQuery(domain, endPoint, 
                    main_args, filter);

                return $.ajax({
                    type:"GET",
                    url: _args["goTo"],
                    data: _args["filter"]
                });

            },

            insertItem: async function insertI(filter){
                let _temp_obj = {
                    "gsidataportion": gsi,
                    "country": country,
                    "progress": "In Progress"
                };
                endPoint = "createItem?";
                
                // Updatating the object, compact two dictionaries
                Object.assign(filter, _temp_obj);
                _args = editParams(domain, endPoint, filter)

                await  $.ajax({
                    type:"POST",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },
            
            deleteItem : (filter) =>{
                endPoint = "deleteItem?";

                _args = editParams(domain, endPoint, filter)

                console.log(_args["goTo"])
                console.log(_args["filter"])

                $.ajax({
                    type:"DELETE",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },

            updateItem : (filter) => {
                endPoint = "updateItem?";
                
                _args = editParams(domain, endPoint, filter)

                console.log(_args["goTo"])
                console.log(_args["filter"])

                $.ajax({
                    type:"PUT",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },
        },

        width: "100%",
        height: "auto", /*400px*/
        
        filtering: true,
        inserting: true,
        editing: true,
        sorting: true,
        paging: true,
        
        pageSize: 10,
        pageButtonCount: 5,

        data: staticData,

        fields: [
            { 
                name:"image", title: "Image", type: "text", width: 100, 
                visible: false,
                cellRenderer : (value, item) => {
                    let img = ` <td align="center"> 
                                    <img src ="${value}" width="50"> 
                                </td>`
                    return img;
                }
            },
            { name:"url_name", title: "Agency Name", type: "text", width: 150},
            // { name:"date_in", title: "GSI", type: "Date", width: 150, visible:false},
            // { name:"country", title: "Country", type: "text", width: 150, visible:false},
            // { name:"gsidataportion", title: "GSI", type: "text", width: 150, visible:false},
            { name: "pkurl", title:"Url", type: "text", width: 250, validate: "required", editing:false },
            { 
                name: "progress", title:"Progress", type: "text", width: 70, editing:true, inserting:false,
                cellRenderer : (value, item) => {
                    // console.log("render badges"); console.log(value);
                    let l_progreess = "", tag_progress = '<td align="center"> </td>';

                    if (value && value != "None"){
                    
                        if (value == "Completed") l_progreess = "success";
                        else l_progreess = "warning";

                        tag_progress = `
                                        <td align="center">
                                            <span class="badge badge-pill badge-${l_progreess}">
                                                ${value}
                                            </span>
                                        </td>`;
                    }
                        
                  return tag_progress;
                }},
            { type: "control" }
        ]
    });

} // => End of getCountries