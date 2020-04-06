/* Date: March 12, 2020

Dev: franco@systemagency.com
Filename: jsgrid_ig_bio.js

This set of code functions will provide the correct
manipulation over the data inside of the DynamoDB's tables.

Report problems to the developers if you found some issues.
*/

// var domain = "http://0.0.0.0:5000/";
var domain = "http://127.0.0.1:8000/";

function editParams(domain, endPoint, filter){

    let params = "";
    let goTo = "";

    for(var key in filter){
        item = filter[key];
        if (item != "")
            params += `${key}=${item}&`;
    }
    params = params.slice(0,-1);
    goTo = domain + endPoint + params;

    return {
        "goTo": goTo,
        "filter": filter
    };
}

function check_ig_format(ig){
    // TODO: Perform this. Use Regullar Expressions
    if( ig.includes( ".com/") ){
        ig = ig.split(".com/");
        ig = ig[ ig.length - 1 ];
    }

    if( ig.includes("?") )
        ig = ig.split("?")[0];
    
    ig = ig.replace(/[@+/]/g, '')

    return ig;
}

async function jsGrid_getData(gsi){
    var staticRoute = domain + "queryItems" + "?gsidataportion=" + gsi;
    const response = await fetch(staticRoute);
    var staticData = await response.json();
    var endPoint = "";

    $('#jsGrid').jsGrid({    
        
        controller: {
            
            loadData : (filter) => {
                // filter, dictionary with params    
                endPoint = "queryItems?";                
                filter['gsidataportion'] = gsi;
                
                let _args = editParams(domain, endPoint, filter)

                return $.ajax({
                    type:"GET",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },

            insertItem: async function insertI(filter){
                endPoint = "createItem?";
                let _temp_obj = {
                    "gsidataportion": gsi,
                    "img": "https://s3.us-east-2.amazonaws.com/systemagency.com/public/static/ig_img_new_item.jpg",
                    "progress": "In Progress"
                };
                
                // Updating the object, compact two dictionaries
                Object.assign(filter, _temp_obj);
                _args = editParams(domain, endPoint, filter);

                await $.ajax({
                    type:"POST",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },
            
            deleteItem : (filter) =>{
                endPoint = "deleteItem?";

                let _args = editParams(domain, endPoint, filter);

                $.ajax({
                    type:"DELETE",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },

            updateItem : (filter) => {
                endPoint = "updateItem?";
                
                _args = editParams(domain, endPoint, filter);

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
        editing: false,
        sorting: true,
        paging: true,
        
        pageSize: 10,
        pageButtonCount: 5,

        data: staticData,

        fields: [
            { 
                name:"img", title: "Image", type: "text", width: 20, 
                visible: true, editing:false, inserting:false, required:false,
                cellRenderer : (value, item) => {
                    return `<td align="center"> 
                                <img src ="${value}" style="width:150px; border-radius: 50%;">
                            </td>`
                     
                },
                editTemplate: (value, item) => {

                    let center = document.getElementsByClassName("jsgrid-table");

                    center = center[1].getElementsByTagName("tbody")[0];
                    if (!center.hasAttribute("align"))
                        center.setAttribute("align", "center");
                    
                    return `<td align="center"> 
                                <img src ="${value}" style="width:150px; border-radius: 50%;">
                            </td>`
                }
            },
            { 
                name: "pkurl", title:"ig Name", type: "text", width: 25, validate: "required", editing:false,
                cellRenderer : (value, item) => {

                    return `<td class="jsgrid-cell" style="width: 75px;"> 
                                ${ check_ig_format( value ) }
                            </td>`;
                }
            },
            { 
                type: "control", width: 10,
                itemTemplate: function(value, item) {
                    var $result = $([]);
        
                    return $result.add(this._createDeleteButton(item));
                }
            }
        ]
    });

} // => End of jsGrid_getData
