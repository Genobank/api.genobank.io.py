<%include file="components/detail.mako" args="section='Permittees'" />


<html>
  <head>
    <meta charset="utf-8">
    <title>${plc}</title>
    <link rel="stylesheet" href="css/style.css">
  </head>
  <body>
    <div class="container">
      <div class="header">

      </div>

      ## form
      <div class="row">
        <div class="col-7">
          <div class="card">
            <div class="card-header">
              <h3>Permittees</h3>
            </div>
            <div class="card-body">
              <h3>Register a permittee</h3>
              <p>A donor allows permission on their biosample when they activate it. Recipients of all permissions must first register with GenoBank.io.</p>
              <h4>Instructions</h4>
              <ol>
                <li>A laboratory that wants to solve consent management and donor privacy signs up with GenoBank.io</li>
                <li>The laboratory creates a public/private key pair</li>
                <li>Choose an available Permittee ID number in the Fulfillment/Biosamples fil</li>
                <li>Submit the form</li>
                <li>Record to the file</li>
                <li>-> The laboratory registers their public key below</li>
              </ol>
            </div>
          </div>
        </div>
        <div class="col-5">
          <div class="card">
            <div class="card-header">
              <h3>Permittee ID</h3>
            </div>
            <div class="card-body">
              <h3>${plc}</h3>
              <p>${plc}</p>
            </div>
          </div>
      </div>
    </div>
  </body>
</html>