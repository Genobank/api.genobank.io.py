let isIdValid = false;
let isAddressValid = false;
async function check_id(){
  const permitteeId = $('#registerPermitteePermitteeId').val()
  const uri = `${window.API_BASE}/permittees/${permitteeId}`

  let headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
   }
  let response = await fetch(uri, { 
    method: "GET",
    headers: headersList
  });

  let data = await response.status;

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


async function createPermittee(){
  console.log("isvalidID", isIdValid);
  console.log("isAddressValid", isAddressValid);

  if (isIdValid && isAddressValid) {
    console.log("Ambos son validos")
  }
}