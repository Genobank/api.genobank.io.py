let isIdValid = false;
let isAddressValid = false;
async function check_id(){
  const permitteeId = $('#registerPermitteePermitteeId').val()
  const uri = `${window.API_BASE}/permittees/${permitteeId}`
  let response = await fetch(uri, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  if (response.status == 200){
    $("#registerPermitteePermitteeId").removeClass("is-invalid");
    $("#registerPermitteePermitteeId").removeClass("is-valid");
    $("#registerPermitteePermitteeId").addClass("is-invalid");
    isIdValid = false;
  }
  if (response.status == 400){
    $("#registerPermitteePermitteeId").removeClass("is-invalid");
    $("#registerPermitteePermitteeId").removeClass("is-valid");
    $("#registerPermitteePermitteeId").addClass("is-valid");
    isIdValid = true;
  }
}

async function checkAddress(){
  $('#registerPermitteePermitteeAddress').on('blur', async function() {
    const address = $('#registerPermitteePermitteeAddress').val();
    const web3 = new Web3(window.ethereum);
    const success = web3.utils.isAddress(address);
    const cssClass = success ? 'text-success' : 'text-danger';
    const icon = success ? 'fa-check' : 'fa-times';
    const text = success ? 'This address is acceptable.' : 'This is not an Ethereum address.';
    if (success) {
      $('#registerPermitteePermitteeAddress').addClass('is-valid');
      $('#registerPermitteePermitteeAddress').removeClass('is-invalid');
      isAddressValid = true;
    } else {
      $('#registerPermitteePermitteeAddress').addClass('is-invalid');
      $('#registerPermitteePermitteeAddress').removeClass('is-valid');
      isAddressValid = false;
    }
    $('#registerPermitteePermitteeAddressValidation').html(`
      <small class="form-text ${cssClass}">
        <i class="fa ${icon}"></i> ${text}
      </small>
    `);
  });
}

async function registerPermittee(){
  if (isIdValid && isAddressValid) {
    const permitteeId = $('#registerPermitteePermitteeId').val();
    const permitteeAddress = $('#registerPermitteePermitteeAddress').val();
    const appSecret = $('#registerPermitteeApplicationSecret').val();

    const secret = await createPermitteeHMAC(permitteeId, permitteeAddress, appSecret);

    const res = await createPermittee(permitteeId, permitteeAddress, appSecret);

    console.log("res\n",res)
    console.log("Ambos son validos")
    if (res.status=="Failure"){
      $("#registerPermitteeResult").removeClass('bg-success');
      $("#registerPermitteeResult").addClass('bg-danger');
      // let inner = `<p>Error during permittee creation: ${res.status_details.description} </p>`
      // $("#registerPermitteeResult").html(inner)


    }else{
      $("#registerPermitteeResult").removeClass('bg-danger');
      $("#registerPermitteeResult").addClass('bg-success');
      
    }

    let inner = `<b>Permittee ID:</b> ${permitteeId}<br/>
                  <b>Permittee address:</b> ${permitteeAddress}<br/>
                  <b>Permittee secret:</b> ${secret}<br/>
                  <b>Response:</b> ${JSON.stringify(res)}`
    $("#registerPermitteeResult").html(inner)


    // $("#registerPermitteeResult").removeClass('bg-danger');
    // $("#registerPermitteeResult").addClass('bg-success');
    // $("#registerPermitteeResult").html("Correct Data")
    // $("#registerPermitteeResult").show();

  }else{
    $("#registerPermitteeResult").removeClass('bg-success');
    $("#registerPermitteeResult").addClass('bg-danger');
    $("#registerPermitteeResult").html("Invalid data")
    $("#registerPermitteeResult").show();
  }
  // $("#registerPermitteeResult").hide();
}


async function createPermittee(permitteeId, permitteeAddress, appSecret) {
  const permitteeSecret = await createPermitteeHMAC(permitteeId, permitteeAddress, appSecret);
  let bodyContent = new FormData();
  bodyContent.append("id", permitteeId);
  bodyContent.append("address", permitteeAddress);
  bodyContent.append("secret", permitteeSecret);
  bodyContent.append("env", window.ENV)
  const url = `${window.NEWAPIBASE}/create_permitee`;
  return fetch(url, {
    method: 'POST',
    header: {
      'Content-Type': 'application/json'
    },
    body: bodyContent
  }).then((res) => {
    return res.json();
  }).catch((error) => {
    console.error(error);
    return { error: error.message };
  });

  // let data = await response.text()

  // console.log("response \n",data);
}


async function createPermitteeHMAC(permitteeId, permitteeAddress, appSecret) {
  const hmacClaim = `${permitteeId}${permitteeAddress}`;
  const enc = new TextEncoder();
  const key = await window.crypto.subtle.importKey(
      "raw", // raw format of the key - should be Uint8Array
      enc.encode(appSecret),
      { // algorithm details
          name: "HMAC",
          hash: {name: "SHA-256"}
      },
      false, // export = false
      ["sign", "verify"] // what this key can do
  );
  const hmac = await window.crypto.subtle.sign(
    "HMAC",
    key,
    enc.encode(hmacClaim)
  );
  var b = new Uint8Array(hmac);
  return Array.prototype.map.call(b, x => ('00'+x.toString(16)).slice(-2)).join("");
}