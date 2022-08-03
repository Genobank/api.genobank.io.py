<%include file="components/detail.mako" args="section='Permittees'" />
<html>
  <head>
    <meta charset="utf-8">
    <title>${plc}</title>
    <script src="/js/createPermittee.js"></script>
  </head>
  <body>
    <div class="container">
      <div class="header">
      </div>
      ## form
      <div class="row">
        <div class="col-7" style="min-width: 370px;">
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
        <div class="col-5" style="min-width: 370px;">
          <div class="card">
            <div class="card-header">
              <h3>Create Permittee</h3>
            </div>
            <div class="card-body">
              <form>
                <div class="form-group">
                  <label>Permittee ID</label>
                  <input type="number" min="0" max="281474976710655" class="form-control" id="registerPermitteePermitteeId" onchange="check_id()">
                </div>
                <div class="form-group">
                  <label>Permittee address</label>
                  <input type="text" class="form-control" id="registerPermitteePermitteeAddress" onchange="checkAddress()">
                </div>
                <div class="form-group">
                  <label>Application Secret</label>
                  <input type="password" class="form-control" id="registerPermitteeApplicationSecret">
                  <small class="form-text text-muted">This same secret is installed on the API server. If you enter the wrong secret here then the operation will fail.</small>
                </div>
                <button type="button" class="btn btn-primary" onclick="login()">Login</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>