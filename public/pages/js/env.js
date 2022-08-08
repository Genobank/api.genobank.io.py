const url = new URL(location.href);
const test = url.pathname.substr(10, 5) == '/test';
window.ENV = test ? 'test' : 'main';
window.WWW_BASE = test ? 'https://genobank.io/test' : 'https://genobank.io';
window.API_BASE = test ? 'https://api-test.genobank.io' : 'https://api.genobank.io';
window.NAMESPACE = test ? 'io.genobank.test' : 'io.genobank';


// window.NEWAPIBASE = 'http://localhost:8081'

// ceate a validation to check if iam in local or external
window.NEWAPIBASE = 'https://genobank.app'

window.PERMITTEE = test ? 'test_create_permitee':'create_permitee'