/* Designed on October 10th, 2019
First Release on October 22th, 2019

Dev: franco@systemagency.com

This piece of software will contain many of the routines need it by
the whole internal site for System Agency (botsactions.systemagency.com)

If some issue detected, plese report it to the Developer.
*/

const domain = "http://0.0.0.0:5000/";

async function getCountries_auth(selectorOfTheGrid, country){
    var staticRoute = domain + "queryItems?country=" + country

    const response = await fetch(staticRoute);
    var staticData = await response.json();

    var endPoint = "";

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

    $(selectorOfTheGrid).jsGrid({    
        
        controller: {
            
            loadData : (filter) => {
                // filter, dictionary with params    
                endPoint = "queryItems?";
                filter["country"] = country;

                _args = editParams(domain, endPoint, filter)

                console.log(_args["goTo"])
                console.log(_args["filter"])

                return $.ajax({
                    type:"GET",
                    url: _args["goTo"],
                    data: _args["filter"]
                });

            },

            insertItem: async function insertI(filter){
                endPoint = "createItem?";
                
                filter["country"] = country;
                filter["gsidataportion"] = "agency";
                filter["progress"] = "In Progress";
                
                _args = editParams(domain, endPoint, filter)

                console.log(_args["goTo"])
                console.log(_args["filter"])

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
            { name:"date_in", title: "GSI", type: "Date", width: 150, visible:false},
            { name:"country", title: "Country", type: "text", width: 150, visible:false},
            { name:"gsidataportion", title: "GSI", type: "text", width: 150, visible:false},
            { name: "pkurl", title:"Url", type: "text", width: 250, validate: "required", editing:false },
            { 
                name: "progress", title:"Progress", type: "text", width: 70, validate: "required", editing:false, inserting:false,
                cellRenderer : (value, item) => {
                    let l_progreess = "warning", tag_progress = '<td align="center"> </td>';
                    
                    if (value){
                        if (value == "Completed") 
                            l_progreess = "success";
                            
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

async function log_out(){
    console.log("log_out");

    var goTo = domain + "logout";

    await $.ajax({
        type:"GET",
        url: goTo
    });

    window.location.replace(domain);
}

function new_country(){
    let add_country = document.getElementById('newCountry').value,
        find = "heading"+add_country, _continue = true;
    
    if(add_country != '' && document.getElementById(find) == undefined){
        country_body = `<div class="card">
            <div class="card-header"  id="heading${add_country}">
                <h2 class="mb-0">
                    <button 
                        class="btn btn-link collapsed" 
                        type="button" 
                        data-toggle="collapse" 
                        data-target="#collapse${add_country}" 
                        aria-expanded="false" 
                        aria-controls="collapse${add_country}" 
                        onclick="getCountries_auth('#jsGrid${add_country}', '${add_country}')">
                        ${add_country}
                    </button>
                    <button type="button" class=" float-right btn btn-warning" onclick="delete_card('heading${add_country}')">Delete</button>
                </h2>
            </div>
                <div id="collapse${add_country}" class="collapse" aria-labelledby="heading${add_country}" data-parent="#accordionCountry">
                    <div id="jsGrid${add_country}"></div>
                </div>
            </div>            
        </div>`

        document.getElementById('accordionCountry').innerHTML += country_body;
    }
    else{
        // Repeated element or empty 
        console.log("It is not possible to add a new country.");
    }
}

async function delete_card(target){
    let goTo = domain.concat('deleteCountry?', 'country=', target.replace('heading', ''));
    document.getElementById(target).remove();
    
    await $.ajax({
        type:"DELETE",
        url: goTo
    });
}

async function reset_pass(){
    let email = document.getElementById("email").value;
    let newPass = document.getElementById("password").value;

    if (email.length > 0){
        if (newPass.length > 0){
            let SHA256 =  new Hashes.SHA256
            newPass = SHA256.hex(newPass)  
            
            console.log('goog password')
            console.log(newPass)
            let endPoint = "updatePass?";
            let goTo = domain + endPoint.concat(
                    'email=', email, '@systemagency.com',
                    '&password=', newPass);

            console.log(goTo)

            await $.ajax({
                type:"PUT",
                url: goTo
            });

            window.location.replace(domain);
        }
    }
}
