/* Designed on October 10th, 2019
First Release on October 22th, 2019

Dev: franco@systemagency.com

This piece of software will contain many of the routines need it by
the whole internal site for System Agency (botsactions.systemagency.com)

If some issue detected, plese report it to the Developer.
*/

// var domain = "http://0.0.0.0:5000/";
var domain = "http://127.0.0.1:8000/";


async function log_out(){
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
