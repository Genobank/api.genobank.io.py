const url = new URL(location.href);
const test = url.pathname.substr(10, 5) == '/test';
const local = (url.hostname == 'localhost' || url.hostname == '127.0.0.1')
window.HOST = url.host
window.ENV = test ? 'test' : 'main';
window.WWW_BASE = test ? 'https://genobank.io/test' : 'https://genobank.io';
window.WWW_BASE = local ? "http://127.0.0.1:5500/test" : window.WWW_BASE 
// window.WWW_LOCAL_BASE = "http://127.0.0.1:5500/test"
window.API_BASE = test ? 'https://api-test.genobank.io' : 'https://api.genobank.io';
window.NAMESPACE = test ? 'io.genobank.test' : 'io.genobank';

window.BIOSAMPLE_ACTIVATION_BASE = test ? [
  `${window.WWW_BASE}/activate`,
] : [
  `${window.WWW_BASE}/activate`,
  `https://start.somosancestria.com`,
];


console.log(window.HOST)
window.favicon = test ? './../static/images/favicon-32x32.png':'./static/images/favicon-32x32.png';

// window.NEWAPIBASE = 'http://localhost:8081'

// ceate a validation to check if iam in local or external
window.NEWAPIBASE = 'https://genobank.app'

window.PERMITTEE = test ? 'test_create_permitee':'create_permitee'