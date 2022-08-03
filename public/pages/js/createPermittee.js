async function check_id(){
  const permitteeId = $('#registerPermitteePermitteeId').val()
  const uri = `${window.API_BASE}/permittees/${permitteeId}`

  console.log(window.API_BASE)
  let headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
   }
  let response = await fetch(uri, { 
    method: "GET",
    headers: headersList
  });

  let data = await response.status;
  console.log(data);

  if (response.status == 200){
    $("#registerPermitteePermitteeId").removeClass("is-invalid");
    $("#registerPermitteePermitteeId").removeClass("is-valid");

    $("#registerPermitteePermitteeId").addClass("is-invalid");
  }
  if (response.status == 400){
    $("#registerPermitteePermitteeId").removeClass("is-invalid");
    $("#registerPermitteePermitteeId").removeClass("is-valid");

    $("#registerPermitteePermitteeId").addClass("is-valid");
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
    } else {
      $('#registerPermitteePermitteeAddress').addClass('is-invalid');
      $('#registerPermitteePermitteeAddress').removeClass('is-valid');
    }
    $('#registerPermitteePermitteeAddressValidation').html(`
      <small class="form-text ${cssClass}">
        <i class="fa ${icon}"></i> ${text}
      </small>
    `);
  });
}

// async function checkAddress(){
//   const address = $("#registerPermitteePermitteeAddress").val()
//   const prefix = address.substring(0, 2);

//   if (prefix == "0x" && address.length == 42){
//     try{
//       parseInt(address,16)
//       $("#registerPermitteePermitteeAddress").removeClass("is-invalid");
//       $("#registerPermitteePermitteeAddress").removeClass("is-valid");

//       $("#registerPermitteePermitteeAddress").addClass("is-valid");
//     }catch{
//       $("#registerPermitteePermitteeAddress").removeClass("is-invalid");
//       $("#registerPermitteePermitteeAddress").removeClass("is-valid")

//       $("#registerPermitteePermitteeAddress").addClass("is-invalid");


//     }
    

//   }else{
//     $("#registerPermitteePermitteeAddress").removeClass("is-invalid");
//     $("#registerPermitteePermitteeAddress").removeClass("is-valid")

//     $("#registerPermitteePermitteeAddress").addClass("is-invalid");

//   }
// }