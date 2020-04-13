/* Date: March 12, 2020

Dev: franco@systemagency.com
Filename: jsgrid_sa_signature.js

This set of code functions will provide the correct
manipulation over the data inside of the DynamoDB's tables.

Report problems to the developers if you found some issues.
*/

// var domain = "http://botsactions.systemagency.com/";
var domain = "/";
var g_gsi = "";


function copySignatureUrl(){
    let temp_text_area = "";
    document.getElementById("modal_temp_text_area").removeAttribute("style");

    temp_text_area = document.getElementById("temp_text_area");
    temp_text_area.select();
    document.execCommand("copy");
    console.log("copy end");
    
    // Add a tittle to the button, notifying that the url was copied
    sign_button = document.getElementById("modal_signature_url");
    sign_button.textContent = "Copied!";

    document.getElementById("modal_temp_text_area").
        setAttribute("style", "display: none;");
}

// action = ["show", "hide"]
function popoverHandler(action){
    let _attr_popover = document.getElementById("modal_signature_url");

    // If the button it avaliable go to the copy and the message popover
    if(!_attr_popover.hasAttribute("disabled")){

        if(action=="show"){
            _attr_popover.setAttribute("title", "Signature Url Copied.");
            copySignatureUrl();
        }
            
        $('#modal_signature_url').popover(action);
    }
    _attr_popover.setAttribute("title", "Signature avaliable.");
}


// filter, dictionary with params
// delete_kyes, list of properties to delete over the object "filter"
//
// The get empty argument will create a list of keys with empty values
// in this way the endpoint can delete empty attrs from the DB
function editParams(domain, endPoint, filter, delete_keys=[], get_empty=false){

    let params = "", empty_attrs = [];

    if (delete_keys != [])
        delete_keys.forEach(del =>{
            if (filter.hasOwnProperty(del)) delete filter[del];
        });

    if (get_empty == true){
        Object.keys(filter).forEach( key => {
            if (typeof(filter[key]) == "string" && filter[key] == "")
                empty_attrs.push( key ); });
        
        if (empty_attrs.length > 0)
            filter["delete_item"] = empty_attrs;
    }
    
    Object.keys(filter).forEach( key => {
        params += `${key}=${filter[key]}&`;
    });

    return {
        // "goTo": encodeURI( domain + endPoint + params.slice(0,-1) ),
        "goTo": domain + endPoint + params.slice(0,-1),
        "filter": filter,
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

function change_preview(item){
    // Turn on the Signature Preview over the frontend.
    
    let preview_data = {
        "img" : document.getElementById('signature_img_holder'),
        "name": document.getElementById('signature_name_holder'),
        "position": document.getElementById('signature_position_holder'),
        "number": document.getElementById('signature_num_holder'),
        "number2": document.getElementById('signature_num_holder_2')
    }, display_opt = "";

    // Obligatory Data
    preview_data.img.setAttribute( "src", item["image"] );
    preview_data.name.textContent = item["worker_name"].toUpperCase();
    preview_data.number.textContent = item["phone"];

    // Optional Data, for that, it is necessary a null check before set it.
    if (item["position"] != undefined){
        _temp_pos = String(item["position"])
        preview_data.position.textContent = _temp_pos.toUpperCase();
    }

    // If the item have second phone number then, display it
    if (item["phone_two"] != undefined)
        preview_data.number2.textContent = item["phone_two"];
    else
        if (preview_data.number2.style["display"] == "")
            display_opt = "none";
        
    preview_data.number2.style["display"] = display_opt;
}

async function getResource(gsi, endPoint = "queryItems"){
    // domain, const of the script.

    let ref = domain + endPoint + gsi;
    let response_sign_t = await fetch(ref);

    // example of ref: queryItems?gsidataportion=sa_signature_type
    return await response_sign_t.json();
}

/**
    * Value extractor from the pop up modal.
    * 
    * @param {String} output ["", "values", "all values"]
    * Every value asociatied will indidcate a diff. functionality,
    * ""; will return just the html objtect
    * "values"; will return just the non empty values
    * "all values"; will return all the values even if they are empty
    * @return {Object}
 */
function fetchModal(output="", clear=false){

    let _output  = {
        "pkurl": document.getElementById("modal_pkurl"),
        "worker_name": document.getElementById("modal_worker_name"),
        "phone": document.getElementById("modal_phone"),
        "signature_type": document.getElementById("modal_signature_type"),
        "select_for_msg": document.getElementById("modal_select_for_msg"),
        "ig": document.getElementById("modal_ig"),
        "phone_two": document.getElementById("modal_phone_two"), 
        "position": document.getElementById("modal_position"),
        "country": document.getElementById("modal_country")
    };
    
    if (output != "" && !clear){
        // sending non empty values
        let comp = "";
        Object.keys(_output).forEach( key => {
            if ( key == "signature_type" ){ // section tag
                i = _output[key].selectedIndex;
                comp = _output[key].options[i].textContent;
            }
            else
                if (key == "select_for_msg")
                    comp = _output[key].getAttribute("status") == "active";
                else 
                    comp = _output[key].value;
            
            if (output == "values" && comp != undefined)
                // just non empty / undefined vals.
                _output[key] = comp;
            else 
                if (output == "all values") // every value
                    _output[key] = comp;
        });
    }else{
        if(clear){
            // console.log("Clean modal")
            Object.keys(_output).forEach(key => {
                if(key == "select_for_msg")
                    editMsgStatus(status="inactive") // check this
                else
                    if(key == "signature_type"){

                        for (let i = 0; i < _output[key].options.length; i++)
                            if (_output[key].options[i].hasAttribute("selected"))
                                _output[key].options[i].removeAttribute("selected")

                        _output[key].options[0].setAttribute("selected", "");
                    }
                        
                    else
                        if (key == "pkurl")
                            _output[key].removeAttribute("disabled")
                        
                        _output[key].value = ""
            });
        }
    }

    return _output;
}

/**
    * Helper to fetch data from DB's item and posted inside
    * at the pop up modal.
    * 
    * This function will handle insertions and editions of entities.
    * 
    * Arguments:
    * 
    * @param {Object} item: {} dictionary with data
    * @param {String} item_handler: ["show.create", "show.edit", 
    * "show.edit.send", "show.create.send"]
    * @return {null}
*/
async function modalHandler(item, exec_route=""){

    let modal_title = document.getElementById("modal_title_name");
    let modal_cont = "", end_point = "";
    let auto_comp = document.getElementById("modal_pkurl_autocomplete");
    let _btn = document.getElementById("button_form_submit");
    let sign_button = document.getElementById("modal_signature_url");
    
    if( exec_route.includes("show")){
        action = "show";

        if (exec_route == "show.create"){
            // Edit the buttom to create a member
            _btn = document.getElementById("button_form_submit");
            _btn.setAttribute("onclick", "modalHandler({}, 'show.create.send');");

            // The email autocomplete will appeare
            auto_comp.style["display"] = "";

            // The url signature button it is disabled
            sign_button.setAttribute("disabled", "");

            // Back the predefine name to the sing button
            sign_button.textContent = "Sign. Url";

            // Clear the modal.
            modal_cont = fetchModal("", true);

            // The s3 attreibute need to be out

            // Edit the modal tittle
            modal_title.textContent = "New Signature";
        }else{
            if (exec_route == "show.edit"){
                // Back the predefine name to the singature button
                sign_button.textContent = "Sign. Url";

                // Edit the buttom to edit a member
                _btn.setAttribute("onclick", "modalHandler({}, 'show.edit.send');");

                // Add the signature url into an attr over the modal
                if (item["s3_file"]) {
                    document.getElementById("temp_text_area").value = item['s3_file'];
                    sign_button.setAttribute("title", 'Signature avaliable.');

                    // And enable the button for copy the signature
                    sign_button.removeAttribute('disabled');
                }

                modal_cont = fetchModal("");

                // The email autocomplete will disappear
                auto_comp.style["display"] = "none";

                // Select the signature that correspond to the member in the modal
                document.getElementById(item["signature_name"].replace(/ /g, ".")).
                    setAttribute("selected", "");
    
                // Edit the modal tittle
                modal_title.textContent = "Editing " + item.worker_name.split(" ")[0] +
                    "'s Signature";
                
                // item's values will be placed into the modal's text inputs
                Object.keys(modal_cont).forEach(item_k =>{
                    modal_k = "modal_" + item_k;
    
                    if( item_k != "select_for_msg" && item_k != "signature_type" ){
    
                        modal_cont[item_k].value = (item[item_k] ? item[item_k] : "");
    
                        if ( item_k == "pkurl" )
                            modal_cont[item_k].setAttribute("disabled", "");
                    }else{
                        if (item_k == "select_for_msg"){
                            //change for first time to green dot
                            editMsgStatus(status=
                                (item[ item_k ]== true ? "active" : "inactive"));
                        }
                    }
                });   
            }
        }
    }
    
    if(exec_route.includes("send")){

        // Hide the modal after make click
        action = "hide";
        sign_img = "https://s3.us-east-2.amazonaws.com/systemagency.com/public";

        modal_cont = fetchModal("all values");

        // Adding the signature image that correspong with the sign. type
        if (modal_cont["signature_type"] == "Jovovich")
            sign_img = sign_img + "/logo-jovovich.png";
        else
            sign_img = sign_img + "/SYSTEM+AGENCY.png";
        modal_cont["image"] = sign_img;

        if (exec_route == "show.edit.send"){
            end_point = "updateItem?";
            type = "PUT";
        }else{
            if (exec_route == "show.create.send"){
                end_point = "createItem?";
                type = "POST";

                // change the property name 'signature_type' for 'signature_name'
                modal_cont["signature_name"] = modal_cont["signature_type"];
                delete modal_cont["signature_type"];

                // Add '@system..'. into the pkurl value before activate the ajax
                modal_cont["pkurl"] = modal_cont["pkurl"] + "@systemagency.com";
            }
        }
        // If PUT, delete empty values
        get_empty = (type == "PUT")

        modal_cont["gsidataportion"] = g_gsi;
        _args = editParams(domain, end_point, modal_cont, [], get_empty);

        console.log(_args);

        await $.ajax({
            type:   type,
            url:    _args["goTo"],
            data:   _args["filter"]
        });

        if (type == "POST"){
            // Showing the new member from a query
            console.log("Welcome ", _args["filter"]["worker_name"]);          
        }
        await $("#jsGrid").jsGrid("loadData", {
            "worker_name": _args["filter"]["worker_name"]});  
            
        // back the button to the normal
        _btn.setAttribute("onclick", "$.noop");
    }

    $('#modalCentered').modal(action);    
} // End of modalHandler

async function fillSignatureTypes(){
    // Fill the select html's tag on the modal over the front end

    let option = "", i = 0,
        _data_container = [],
        _destiny_data = [],
        _data = await getResource('?gsidataportion=sa_signature_type'),
        _destiny = document.getElementById("modal_signature_type");

    
    _data.forEach( _ => {
        _data_container.push( {
            "pkurl": _["pkurl"],
            "signature_name": _["signature_name"]
        });
        
        if ( ++i < _destiny.options.length)
            _destiny_data.push( _destiny.options[i].text );

        // i++;
    });

    i = 0;

    _data_container.forEach( _ =>{
        if ( _destiny_data.includes( _["signature_name"] ) == false ){
            option = document.createElement("option");
            option.setAttribute("value", i++); // Signature's Key name
            option.setAttribute("id", _["signature_name"].replace(/ /g, ".")); // Signature's Key name 
            option.text = _.signature_name;

            _destiny.add(option);
        }
        // i++;
    });
}

// status = ["active", "inactive"]
function editMsgStatus(status){
    let _dot = document.getElementById("modal_select_for_msg");
    
    if (status == "")
        status = (_dot.getAttribute("status") == "active" ? 
            "inactive" : "active");
    
    if (status == "active"){
        // status say inactive, go to inactive, go to 'else'
        _dot.setAttribute("class", "dot dot_green");
        _dot.setAttribute("status", "active");
        _dot.setAttribute("title", "Selected for Emailing");    
    }else{
        _dot.setAttribute("class", "dot dot_orange");
        _dot.setAttribute("status", "inactive");
        _dot.setAttribute("title", "Not Selected for Emailing");
    }
}

async function jsGrid_getData(gsi){
    
    // Data Mamangement and Data Controller using jsGrid
    g_gsi = gsi;
    var staticData = await getResource("?gsidataportion=" + gsi);
    // console.log(staticData);

    var signatureType = await getResource("?gsidataportion=sa_signature_type");
    // console.log(signatureType);
    
    var endPoint = "";

    $('#jsGrid').jsGrid({    
        
        controller: {
            
            loadData : (filter) => {
                // filter, dictionary with params    
                // console.log("loadData", filter);
                
                // console.log(staticData);
                endPoint = "queryItems?";                
                filter['gsidataportion'] = gsi;
                
                let _args = editParams(
                    domain, endPoint, filter, 
                    delete_items=["select_for_msg"]);
                
                return $.ajax({
                    type:"GET",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            },

            deleteItem : (filter) => {
                endPoint = "deleteItem?";

                let _args = editParams(domain, endPoint, filter);
                console.log( _args )

                // Back to the all rows
                $("#jsGrid").jsGrid("loadData");

                return $.ajax({
                    type:"DELETE",
                    url: _args["goTo"],
                    data: _args["filter"]
                });
            }
        },

        width: "100%",
        height: "auto", /*400px*/
        
        filtering: true,
        editing: true,
        sorting: true,
        paging: true,
        
        pageSize: 10,
        pageButtonCount: 5,

        data: staticData,

        fields: [
            { 
                name: "worker_name", title:"Name", type: "text", width: 10, validate: "required",
                editing:true
            },
            { 
                name: "signature_name", title: "Signature", type: "text", width: 8, 
                editing:true, filtering: true,
                items: signatureType, valueField: "signature_name", textField: "signature_name",
                cellRenderer : (value, item) => {
                    let _type = "success";

                    if (value == "Long Term")
                        _type = "primary";
                    else
                        if (value == "Jovovich")
                            _type = "secondary";


                    return `<td align="center">
                                <span class="badge badge-${_type}">${value}</span>
                            </td>`;
                }
            },
            { 
                name: "select_for_msg", type: "checkbox", title: "Message", width: 1, 
                filtering: true, sorting:true
            },
            { 
                type: "control", width: 5,
                modeSwitchButton: false,
                // editButton: false,
                headerTemplate: function() {
                    
                    return $("<input>")
                                .attr("class", "jsgrid-button jsgrid-mode-button jsgrid-insert-mode-button")
                                .attr("type", "button")
                                .on("click", function () {
                                    $("#jsGrid").jsGrid("insertItem");
                                });
                }
            }
        ]

        ,rowClick: function(args) {
            // Expose the signature preview
            let sign_display = document.getElementById('signature_preview');
            let _opt = ""

            if (args.item["worker_name"].toUpperCase() != 
                document.getElementById('signature_name_holder').textContent){
                change_preview(item=args.item);
            }else{
                // check diffs names
                (sign_display.style["display"] == "") ?  _opt = "none" : _opt = "";
            }
            sign_display.style["display"] = _opt; 
            
        }

        ,insertItem: () =>{
            modalHandler({}, "show.create");
        }

        ,editItem: (args) =>{
            // Passing the args from the actual Row
            args["gsidataportion"] = gsi;
            modalHandler(args, "show.edit");
        }
    });

} // => End of jsGrid_getData
