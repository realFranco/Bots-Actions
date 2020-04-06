/* Designed on October 10th, 2019
First Release on October 22th, 2019

Dev: franco@systemagency.com

This piece of software will contain many of the routines need it by
the whole internal site for System Agency (botsactions.systemagency.com)

If some issue detected, plese report it to the Developer.
*/

// const domain = "http://0.0.0.0:5000/";
const domain = "http://127.0.0.1:8000/";

async function getCountries(selectorOfTheGrid, country){

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

            insertItem: $.noop,
            
            deleteItem : $.noop,

            updateItem : $.noop,
        },

        width: "100%",
        height: "auto", /*400px*/
        
        filtering: true,
        inserting: false,
        editing: false,
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
            { name: "pkurl", title:"Url", type: "text", width: 250, validate: "required", editing:false }
        ]
    });

} // => End of getCountries

async function log_in(){
    var goTo = domain.concat("login");
    var email = document
                    .getElementById("email")
                    .value
                    .split("@")[0]
                    .concat("@systemagency.com"),
                password = document
                            .getElementById("password")
                            .value;

    var SHA256 = new Hashes.SHA256
    password = SHA256.hex(password)

    await $.ajax({
        type:"POST",
        url: goTo,
        headers: {
            "Email": email,
            "Password": password
        }
    });
    window.location.replace(domain);
}

async function sing_in(){
    var goTo = domain.concat("registerUser");
    var email = document
                    .getElementById("email")
                    .value
                    .split("@")[0]
                    .concat("@systemagency.com"),
                password = document
                            .getElementById("password")
                            .value;

    var SHA256 =  new Hashes.SHA256
    password = SHA256.hex(password)

    out = $.ajax({
        type:"PUT",
        url: goTo
        , headers: {
            "Email": email,
            "Password": password
        }
    });   
    await out;
    
    window.location.replace(domain);
}
