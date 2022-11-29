import users from '/static/data.json' assert {type: 'json'};

//console.log(users);

function payWithPaystack(){        
    var handler = PaystackPop.setup({
        key: users["SECRET_KEY"],
        email: users["EMAIL"],
        amount: users["AMOUNT"],
        ref: users["RANDOM_REF"], // generates a pseudo-unique reference. Please replace with a reference you generated. Or remove the line entirely so our API will generate one for you
        metadata: {
        custom_fields: [
            {
                display_name: "Mobile Number",
                variable_name: "mobile_number",
                value: users["PHONE_NUMBER"]
            }
        ]
        },
        callback: function(response){
            alert('success. transaction ref is ' + response.reference);
        },
        onClose: function(){
            alert('window closed');
        }
    });
    handler.openIframe();
    };

payWithPaystack()